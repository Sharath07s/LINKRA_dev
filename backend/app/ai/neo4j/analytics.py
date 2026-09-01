import logging
from typing import Dict, List, Any
from app.db.neo4j import neo4j_conn

logger = logging.getLogger(__name__)

class Neo4jAnalyticsService:
    def __init__(self):
        self.get_session = neo4j_conn.get_session

    def get_entity_degree(self, entity_id: str) -> Dict[str, Any]:
        query = """
        MATCH (e:Entity {id: $entity_id})
        OPTIONAL MATCH (e)-[r_out]->()
        WITH e, count(r_out) AS out_degree
        OPTIONAL MATCH (e)<-[r_in]-()
        WITH e, out_degree, count(r_in) AS in_degree
        RETURN out_degree + in_degree AS total_degree, in_degree, out_degree
        """
        with self.get_session() as session:
            result = session.run(query, entity_id=entity_id)
            record = result.single()
            if not record:
                return {"total_degree": 0, "in_degree": 0, "out_degree": 0}
            return {
                "total_degree": record["total_degree"] or 0,
                "in_degree": record["in_degree"] or 0,
                "out_degree": record["out_degree"] or 0
            }

    def get_degree_centrality(self, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
        MATCH (n:Entity)-[r]-()
        WITH n, count(r) AS degree
        RETURN n.id AS entity_id, n.name AS name, n.entity_type AS type, degree
        ORDER BY degree DESC
        LIMIT $limit
        """
        with self.get_session() as session:
            result = session.run(query, limit=limit)
            return [dict(record) for record in result]

    def get_shortest_path(self, source_id: str, target_id: str, max_depth: int = 4) -> Dict[str, Any]:
        # Using a bounded shortest path query
        query = f"""
        MATCH path = shortestPath((a:Entity {{id: $source_id}})-[*..{max_depth}]-(b:Entity {{id: $target_id}}))
        RETURN path
        """
        with self.get_session() as session:
            result = session.run(query, source_id=source_id, target_id=target_id)
            record = result.single()
            if not record or not record.get("path"):
                return {"path_exists": False, "length": 0, "nodes": [], "edges": []}
            
            path = record["path"]
            
            # Format nodes
            formatted_nodes = []
            for n in path.nodes:
                labels = list(n.labels)
                labels = [l for l in labels if l != "Entity"]
                label = labels[0] if labels else "Unknown"
                
                formatted_nodes.append({
                    "id": str(n.get("id", n.element_id)),
                    "label": n.get("name") or n.get("title") or f"{label}_{n.element_id}",
                    "type": label.lower(),
                })
                
            # Format edges
            formatted_edges = []
            for r in path.relationships:
                formatted_edges.append({
                    "source": str(r.start_node.get("id", r.start_node.element_id)),
                    "target": str(r.end_node.get("id", r.end_node.element_id)),
                    "relation": r.type,
                })
                
            return {
                "path_exists": True,
                "length": len(path.relationships),
                "nodes": formatted_nodes,
                "edges": formatted_edges
            }

    def get_relationship_distribution(self, entity_id: str) -> List[Dict[str, Any]]:
        query = """
        MATCH (n:Entity {id: $entity_id})-[r]-()
        RETURN type(r) AS rel_type, count(r) AS count
        ORDER BY count DESC
        """
        with self.get_session() as session:
            result = session.run(query, entity_id=entity_id)
            return [dict(record) for record in result]
            
    def get_local_component(self, entity_id: str, max_depth: int = 5) -> Dict[str, Any]:
        """Bounded component calculation for Aura Free."""
        query = f"""
        MATCH (e:Entity {{id: $entity_id}})-[*1..{max_depth}]-(connected:Entity)
        RETURN count(distinct connected) + 1 AS component_size
        """
        with self.get_session() as session:
            result = session.run(query, entity_id=entity_id)
            record = result.single()
            if not record:
                return {"component_size": 1}
            return {"component_size": record["component_size"] or 1}

neo4j_analytics = Neo4jAnalyticsService()
