import logging
from typing import Dict, Any, List
from neo4j import GraphDatabase

from app.schemas.graph import CommunityResponse, Community, CommunityMember
from app.core.config import settings

logger = logging.getLogger(__name__)

class Neo4jCommunityAnalytics:
    """
    Handles graph community detection capabilities using Neo4j GDS on AuraDB Free.
    Uses direct session execution of gds.graph.project and gds.louvain.stream.
    """

    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.driver = None

    def _get_driver(self):
        if not self.driver:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        return self.driver

    def get_communities(self, algorithm: str = "louvain") -> CommunityResponse:
        """
        Compute graph communities using Louvain or Leiden on the real graph.
        """
        logger.info(f"Community detection requested using {algorithm}.")
        
        try:
            driver = self._get_driver()
            with driver.session(database=self.user) as session:
                # 1. Drop existing projection if any
                try:
                    session.run("CALL gds.graph.drop('linkra_community_graph', false)")
                except Exception:
                    pass

                # 2. Project the graph with inline memory parameter
                logger.info("Projecting graph for community detection...")
                session.run("""
                    CALL gds.graph.project(
                        'linkra_community_graph',
                        '*',
                        '*',
                        {
                            undirectedRelationshipTypes: ['*'],
                            memory: '2GB'
                        }
                    )
                """)

                # 3. Run algorithm
                logger.info(f"Running {algorithm} algorithm...")
                if algorithm.lower() == "leiden":
                    proc_call = "CALL gds.leiden.stream('linkra_community_graph')"
                else:
                    proc_call = "CALL gds.louvain.stream('linkra_community_graph')"

                result = session.run(f"""
                    {proc_call}
                    YIELD nodeId, communityId
                    RETURN gds.util.asNode(nodeId).id AS entity_id,
                           gds.util.asNode(nodeId).name AS name,
                           labels(gds.util.asNode(nodeId))[0] AS type,
                           communityId
                    ORDER BY communityId, entity_id
                """)

                # 4. Process results
                communities_dict: Dict[int, List[CommunityMember]] = {}
                for record in result:
                    cid = record["communityId"]
                    member = CommunityMember(
                        entity_id=record["entity_id"] or "unknown",
                        name=record["name"] or "Unknown Entity",
                        type=record["type"] or "Unknown"
                    )
                    if cid not in communities_dict:
                        communities_dict[cid] = []
                    communities_dict[cid].append(member)

                # 5. Format response
                communities_list = []
                for cid, members in communities_dict.items():
                    communities_list.append(
                        Community(
                            community_id=str(cid),
                            size=len(members),
                            members=members
                        )
                    )

                # 6. Cleanup projection
                session.run("CALL gds.graph.drop('linkra_community_graph', false)")

                return CommunityResponse(
                    status="success",
                    message=f"Graph community detection completed using {algorithm}.",
                    algorithm=algorithm.lower(),
                    communities=communities_list
                )
        except Exception as e:
            logger.error(f"Failed to execute GDS community detection: {e}", exc_info=True)
            return CommunityResponse(
                status="ERROR",
                message=f"Failed to compute communities: {str(e)}",
                algorithm=algorithm.lower(),
                communities=[]
            )
        finally:
            # We don't close the driver here so it can be reused, or we could handle it via lifecycle
            pass

neo4j_community = Neo4jCommunityAnalytics()
