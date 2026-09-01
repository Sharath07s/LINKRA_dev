import logging
from typing import Dict, List, Any
from app.db.neo4j import neo4j_conn
from app.ai.neo4j import cypher_queries as queries

logger = logging.getLogger(__name__)

class Neo4jIntelligenceService:
    def __init__(self):
        self.get_session = neo4j_conn.get_session

    def initialize_constraints(self) -> None:
        """Ensure Neo4j index/constraint for Entity.id exists. Called at app startup."""
        try:
            with self.get_session() as session:
                session.run(queries.ENSURE_ENTITY_CONSTRAINT)
                logger.info("Neo4j Entity.id constraint verified.")
        except Exception as e:
            logger.warning(f"Could not initialize Neo4j constraints (DB may be unavailable): {e}")

    def find_associates(self, entity_id: str) -> List[Dict[str, Any]]:
        with self.get_session() as session:
            result = session.run(queries.FIND_ASSOCIATES, entity_id=entity_id)
            return [dict(record) for record in result]

    def find_shared_vehicles(self, entity_id: str) -> List[Dict[str, Any]]:
        with self.get_session() as session:
            result = session.run(queries.FIND_SHARED_VEHICLES, entity_id=entity_id)
            return [dict(record) for record in result]

    def find_crimes_by_vehicle(self, vehicle_number: str) -> List[Dict[str, Any]]:
        with self.get_session() as session:
            result = session.run(queries.FIND_CRIMES_FOR_VEHICLE, vehicle_number=vehicle_number)
            return [dict(record) for record in result]

    def find_repeat_offenders(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self.get_session() as session:
            result = session.run(queries.FIND_REPEAT_OFFENDERS, limit=limit)
            return [dict(record) for record in result]

    def get_suspect_network(self, entity_id: str) -> Dict[str, Any]:
        with self.get_session() as session:
            result = session.run(
                queries.GET_NETWORK_NODES_EDGES,
                entity_id=entity_id,
                limit=queries.DEFAULT_NETWORK_LIMIT
            )
            record = result.single()
            if not record:
                return {"nodes": [], "edges": []}
            return self._format_graph_data(record["nodes"], record["edges"])
            
    def get_entity_neighborhood(self, entity_id: str, depth: int = 2, max_nodes: int = 150) -> Dict[str, Any]:
        """
        Bounded graph traversal for M1.7 API
        """
        if depth == 0:
            query = f"""
            MATCH (e:Entity {{id: $entity_id}})
            RETURN collect(e) AS nodes, [] AS edges
            """
        else:
            query = f"""
            MATCH path = (e:Entity {{id: $entity_id}})-[*1..{depth}]-(connected:Entity)
            WITH path, connected LIMIT {max_nodes}
            UNWIND nodes(path) AS n
            UNWIND relationships(path) AS r
            RETURN collect(distinct n) AS nodes, collect(distinct r) AS edges
            """
            
        with self.get_session() as session:
            result = session.run(query, entity_id=entity_id)
            record = result.single()
            if not record or not record["nodes"]:
                return {"nodes": [], "edges": []}
            return self._format_graph_data(record["nodes"], record["edges"])

    def get_high_risk_network(self, min_risk: float = 8.0, limit: int = 100) -> Dict[str, Any]:
        with self.get_session() as session:
            result = session.run(
                queries.GET_HIGH_RISK_NETWORK,
                min_risk=min_risk,
                limit=limit
            )
            record = result.single()
            if not record:
                return {"nodes": [], "edges": []}
            return self._format_graph_data(record["nodes"], record["edges"])

    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        with self.get_session() as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]

    def sync_canonical_entity(self, entity_id: str, entity_type: str, properties: Dict[str, Any]) -> None:
        """
        Synchronizes a PostgreSQL CanonicalEntity to a Neo4j node idempotently.
        Sets both the base :Entity label and specific type label.
        """
        label_map = {
            "PERSON": "Person",
            "ORGANIZATION": "Organization",
            "LOCATION": "Location",
            "VEHICLE": "Vehicle",
            "PHONE": "PhoneNumber",
            "DATE": "Date",
            "CRIME": "Crime",
            "POLICE_STATION": "PoliceStation"
        }
        sublabel = label_map.get(entity_type, "Unknown")
        
        query = f"""
        MERGE (n:Entity {{id: $id}})
        SET n:{sublabel}, n += $props
        """
        
        with self.get_session() as session:
            session.run(query, id=str(entity_id), props=properties)

    def sync_relationship(self, relationship_id: str, source_id: str, target_id: str, relationship_type: str, properties: Dict[str, Any]) -> None:
        """
        Synchronizes a PostgreSQL EntityRelationship to a Neo4j edge idempotently using its UUID.
        Sanitizes relationship_type to prevent Cypher injection.
        """
        # Security: sanitize type — only allow alphanumeric + underscore
        rel_type = "".join([c for c in relationship_type if c.isalnum() or c == "_"])
        if not rel_type:
            logger.warning(f"Skipping relationship with empty sanitized type: '{relationship_type}'")
            return
        
        query = f"""
        MATCH (a:Entity {{id: $source_id}}), (b:Entity {{id: $target_id}})
        MERGE (a)-[r:{rel_type} {{id: $rel_id}}]->(b)
        SET r += $props
        """
        
        with self.get_session() as session:
            session.run(query, source_id=str(source_id), target_id=str(target_id), rel_id=str(relationship_id), props=properties)

    def _format_graph_data(self, nodes, edges) -> Dict[str, Any]:
        formatted_nodes = []
        formatted_edges = []
        
        # Map Neo4j labels to frontend-friendly type strings
        LABEL_TO_TYPE = {
            "Person": "person",
            "Organization": "organization",
            "Location": "location",
            "Vehicle": "vehicle",
            "PhoneNumber": "phone",
            "Date": "date",
            "Crime": "crime",
            "PoliceStation": "police_station",
        }
        
        for n in nodes:
            labels = list(n.labels)
            labels = [l for l in labels if l != "Entity"]
            label = labels[0] if labels else "Unknown"
            
            formatted_nodes.append({
                "id": str(n.get("id", n.element_id)),
                "label": n.get("name") or n.get("title") or f"{label}_{n.element_id}",
                "type": LABEL_TO_TYPE.get(label, label.lower()),
                "risk": "High" if float(n.get("risk_score", 0)) > 7 else ("Medium" if float(n.get("risk_score", 0)) > 4 else "Low"),
                "rating": float(n.get("risk_score", 5.0)),
                "desc": n.get("entity_type", label)
            })

        for r in edges:
            formatted_edges.append({
                "id": str(r.get("id", r.element_id)),
                "source": str(r.start_node.get("id", r.start_node.element_id)),
                "target": str(r.end_node.get("id", r.end_node.element_id)),
                "relation": r.type,
                "weight": r.get("confidence", 0) * 100 or r.get("weight") or 80,
                "confidence": float(r.get("confidence", 1.0)),
                "extraction_method": r.get("extraction_method"),
                "source_page": r.get("source_page"),
                "ingestion_job_id": r.get("ingestion_job_id"),
                "desc": f"{r.type} (Conf: {r.get('confidence', 1.0):.2f})"
            })

        return {"nodes": formatted_nodes, "edges": formatted_edges}

neo4j_intelligence = Neo4jIntelligenceService()
