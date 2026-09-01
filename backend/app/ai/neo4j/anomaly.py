import logging
import uuid
from typing import Dict, List, Any, Optional
from app.db.neo4j import neo4j_conn

logger = logging.getLogger(__name__)

class Neo4jAnomalyService:
    def __init__(self):
        self.get_session = neo4j_conn.get_session

    def get_anomalies_for_entity(self, entity_id: str) -> Dict[str, Any]:
        """
        Detect anomalies for a specific entity.
        Returns: Dict with "status", "anomalies", "reason".
        """
        anomalies = []
        
        with self.get_session() as session:
            # 1. Check graph population for baseline safety
            count_query = "MATCH (n:Entity) RETURN count(n) AS total_nodes"
            result = session.run(count_query)
            record = result.single()
            total_nodes = record["total_nodes"] if record else 0
            
            if total_nodes < 5:
                return {
                    "status": "insufficient_data",
                    "anomalies": [],
                    "reason": "At least 5 entities are required for statistical anomaly detection."
                }
                
            # 2. Get Degree Baseline
            baseline_query = """
            MATCH (n:Entity)
            OPTIONAL MATCH (n)-[r]-()
            WITH n, count(r) AS degree
            WITH avg(degree) AS mean_deg, stDev(degree) AS std_deg
            RETURN mean_deg, std_deg
            """
            baseline_res = session.run(baseline_query).single()
            mean_deg = baseline_res["mean_deg"] or 0
            std_deg = baseline_res["std_deg"] or 0
            
            # 3. Get Entity Stats
            entity_query = """
            MATCH (e:Entity {id: $entity_id})
            OPTIONAL MATCH (e)-[r]-()
            RETURN e, count(r) AS total_degree
            """
            entity_res = session.run(entity_query, entity_id=entity_id).single()
            
            if not entity_res or not entity_res["e"]:
                return {
                    "status": "not_found",
                    "anomalies": [],
                    "reason": "Entity not found in graph."
                }
                
            total_degree = entity_res["total_degree"] or 0
            
            # --- Check A: ISOLATED_ENTITY ---
            if total_degree == 0:
                anomalies.append({
                    "anomaly_id": str(uuid.uuid4()),
                    "entity_id": entity_id,
                    "anomaly_type": "ISOLATED_ENTITY",
                    "severity": "LOW",
                    "score": 1.0,
                    "observed_value": 0,
                    "baseline_value": round(mean_deg, 2),
                    "reason": "Entity has zero connections in the graph.",
                    "explanation": {
                        "reason": "Entity has zero observed graph relationships.",
                        "metrics": {
                            "entity_degree": 0
                        },
                        "method": "degree_count",
                        "interpretation": "This entity has no structural connections in the network."
                    }
                })
            
            # --- Check B: HIGH_DEGREE ---
            # If degree > mean + 2*sigma
            if std_deg > 0 and total_degree > (mean_deg + 2 * std_deg):
                # Z-score roughly maps to score
                z_score = (total_degree - mean_deg) / std_deg
                # cap score at 1.0, e.g. z=2 -> 0.8, z=5 -> 0.99
                score = min(0.99, max(0.5, 0.5 + (z_score - 2) * 0.1))
                
                anomalies.append({
                    "anomaly_id": str(uuid.uuid4()),
                    "entity_id": entity_id,
                    "anomaly_type": "HIGH_DEGREE",
                    "severity": "HIGH",
                    "score": round(score, 2),
                    "observed_value": total_degree,
                    "baseline_value": round(mean_deg, 2),
                    "reason": "Entity connectivity is statistically significantly higher than the graph baseline.",
                    "explanation": {
                        "reason": "Entity connectivity is unusually high relative to the current graph baseline.",
                        "metrics": {
                            "entity_degree": total_degree,
                            "graph_mean_degree": round(mean_deg, 2),
                            "graph_stddev": round(std_deg, 2),
                            "z_score": round(z_score, 2)
                        },
                        "method": "degree_z_score",
                        "interpretation": "Structural connectivity is unusually high relative to the current graph baseline."
                    }
                })
                
            # --- Check C: RELATIONSHIP_CONCENTRATION ---
            if total_degree >= 5:
                dist_query = """
                MATCH (e:Entity {id: $entity_id})-[r]-()
                RETURN type(r) AS rel_type, count(r) AS count
                ORDER BY count DESC
                LIMIT 1
                """
                dist_res = session.run(dist_query, entity_id=entity_id).single()
                if dist_res:
                    top_count = dist_res["count"]
                    top_rel_type = dist_res["rel_type"]
                    concentration = top_count / total_degree
                    
                    if concentration >= 0.8:
                        anomalies.append({
                            "anomaly_id": str(uuid.uuid4()),
                            "entity_id": entity_id,
                            "anomaly_type": "RELATIONSHIP_CONCENTRATION",
                            "severity": "MEDIUM",
                            "score": round(concentration, 2),
                            "observed_value": round(concentration * 100, 1), # percentage
                            "baseline_value": 0, # not strictly a global baseline comparison
                            "reason": f"Relationships are unusually concentrated ({int(concentration*100)}%) in a single type ({top_rel_type}).",
                            "explanation": {
                                "reason": f"{top_count} of {total_degree} observed relationships are of type {top_rel_type}, representing {round(concentration * 100, 1)}% of this entity's connections.",
                                "metrics": {
                                    "total_degree": total_degree,
                                    "dominant_relationship_type": top_rel_type,
                                    "dominant_relationship_count": top_count,
                                    "concentration_percentage": round(concentration * 100, 1),
                                    "threshold_percentage": 80.0
                                },
                                "method": "relationship_concentration_ratio",
                                "interpretation": f"The entity's connections are highly skewed toward {top_rel_type}."
                            }
                        })
                        
        return {
            "status": "success",
            "anomalies": anomalies,
            "reason": None
        }

    def get_top_anomalies(self, limit: int = 50) -> Dict[str, Any]:
        """
        Global bounded scan for anomalies.
        """
        anomalies = []
        with self.get_session() as session:
            count_query = "MATCH (n:Entity) RETURN count(n) AS total_nodes"
            total_nodes = session.run(count_query).single()["total_nodes"]
            
            if total_nodes < 5:
                return {
                    "status": "insufficient_data",
                    "anomalies": [],
                    "reason": "At least 5 entities are required for statistical anomaly detection."
                }
                
            baseline_query = """
            MATCH (n:Entity)
            OPTIONAL MATCH (n)-[r]-()
            WITH n, count(r) AS degree
            WITH avg(degree) AS mean_deg, stDev(degree) AS std_deg
            RETURN mean_deg, std_deg
            """
            baseline_res = session.run(baseline_query).single()
            mean_deg = baseline_res["mean_deg"] or 0
            std_deg = baseline_res["std_deg"] or 0
            
            # Find HIGH_DEGREE only for now to keep global scan bounded
            if std_deg > 0:
                high_degree_threshold = mean_deg + 2 * std_deg
                scan_query = """
                MATCH (e:Entity)
                OPTIONAL MATCH (e)-[r]-()
                WITH e, count(r) AS degree
                WHERE degree > $threshold
                RETURN e.id AS entity_id, degree
                ORDER BY degree DESC
                LIMIT $limit
                """
                results = session.run(scan_query, threshold=high_degree_threshold, limit=limit)
                
                for record in results:
                    z_score = (record["degree"] - mean_deg) / std_deg
                    score = min(0.99, max(0.5, 0.5 + (z_score - 2) * 0.1))
                    anomalies.append({
                        "anomaly_id": str(uuid.uuid4()),
                        "entity_id": record["entity_id"],
                        "anomaly_type": "HIGH_DEGREE",
                        "severity": "HIGH",
                        "score": round(score, 2),
                        "observed_value": record["degree"],
                        "baseline_value": round(mean_deg, 2),
                        "reason": "Entity connectivity is statistically significantly higher than the graph baseline."
                    })
                    
        return {
            "status": "success",
            "anomalies": anomalies,
            "reason": None
        }

neo4j_anomaly = Neo4jAnomalyService()
