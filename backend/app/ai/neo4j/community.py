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
                node_to_community = {}
                
                for record in result:
                    cid = record["communityId"]
                    eid = record["entity_id"]
                    if not eid:
                        continue
                    member = CommunityMember(
                        entity_id=eid,
                        name=record["name"] or "Unknown Entity",
                        type=record["type"] or "Unknown"
                    )
                    if cid not in communities_dict:
                        communities_dict[cid] = []
                    communities_dict[cid].append(member)
                    node_to_community[eid] = cid

                # Filter out singletons to keep the response clean if needed, but we keep all for now.
                
                # Fetch influential entities and bridges
                # To do this efficiently, we can use a quick cypher match for degrees and external relationships.
                # However, doing it per community can be slow. We will compute it dynamically using Python for the top communities or just do a generic query.
                
                communities_list = []
                for cid, members in communities_dict.items():
                    # Minimum viable graph-structural analysis
                    influential_entity = None
                    bridge_candidates = []
                    rel_count = 0
                    rel_types = set()
                    
                    if len(members) > 1:
                        # Find the most connected node WITHIN the community (Influential Entity)
                        # We use a Cypher query restricted to these member IDs.
                        member_ids = [m.entity_id for m in members]
                        stats_query = """
                        MATCH (n)-[r]-(m)
                        WHERE n.id IN $member_ids AND m.id IN $member_ids
                        RETURN n.id AS eid, count(r) AS degree, collect(DISTINCT type(r)) AS rtypes
                        ORDER BY degree DESC LIMIT 1
                        """
                        stats_result = session.run(stats_query, member_ids=member_ids)
                        for s_rec in stats_result:
                            influential_entity = s_rec["eid"]
                            rel_count = s_rec["degree"] # Just an approximation for the community connectivity
                            for rt in s_rec["rtypes"]:
                                rel_types.add(rt)
                                
                        # Find bridge candidates (nodes connected to outside)
                        bridge_query = """
                        MATCH (n)-[r]-(m)
                        WHERE n.id IN $member_ids AND NOT m.id IN $member_ids
                        RETURN n.id AS eid, count(r) AS ext_degree
                        ORDER BY ext_degree DESC LIMIT 3
                        """
                        bridge_result = session.run(bridge_query, member_ids=member_ids)
                        bridge_candidates = [br["eid"] for br in bridge_result if br["eid"]]

                    communities_list.append(
                        Community(
                            community_id=str(cid),
                            size=len(members),
                            members=members,
                            influential_entity=influential_entity,
                            bridge_candidates=bridge_candidates,
                            relationships=rel_count,
                            relationship_types=list(rel_types),
                            evidence="Computed via graph topology and degree centrality within the projected network."
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
