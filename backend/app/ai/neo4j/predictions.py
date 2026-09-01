import logging
from typing import Dict, List, Any
from app.db.neo4j import neo4j_conn

logger = logging.getLogger(__name__)

class Neo4jPotentialLinkService:
    def __init__(self):
        self.get_session = neo4j_conn.get_session

    def get_potential_links_for_entity(self, entity_id: str, limit: int = 20, min_score: float = 0.4) -> Dict[str, Any]:
        """
        Generate structural potential links for a focal entity.
        Requires >= 2 common neighbors.
        """
        potential_links = []
        
        # We need to cap the maximum number of structural candidates
        # that we evaluate to protect Aura Free memory limits.
        if limit > 50:
            limit = 50
            
        with self.get_session() as session:
            # Check if entity exists and has degree >= 2 (otherwise it can't have 2 common neighbors with anyone)
            check_query = """
            MATCH (a:Entity {id: $entity_id})
            OPTIONAL MATCH (a)-[r]-()
            RETURN a, count(r) as degree
            """
            check_res = session.run(check_query, entity_id=entity_id).single()
            if not check_res or not check_res["a"]:
                return {
                    "status": "not_found",
                    "potential_links": [],
                    "reason": "Entity not found in graph."
                }
            
            if check_res["degree"] < 2:
                return {
                    "status": "insufficient_data",
                    "potential_links": [],
                    "reason": "Entity has insufficient connections to compute structural similarity."
                }

            # Bounded Cypher query to calculate Common Neighbors, Jaccard, and Preferential Attachment
            # 1. Match 2-hop disjoint paths
            # 2. Filter for cn >= 2
            # 3. Fetch A's and B's neighborhood sizes to compute Jaccard & PA
            query = """
            MATCH (a:Entity {id: $entity_id})-[r1]-(common:Entity)-[r2]-(b:Entity)
            WHERE a <> b AND NOT (a)-[]-(b)
            WITH a, b, count(DISTINCT common) as cn
            WHERE cn >= 2
            WITH a, b, cn
            MATCH (a)-[]-(na:Entity)
            WITH a, b, cn, count(DISTINCT na) as degree_a
            MATCH (b)-[]-(nb:Entity)
            WITH a, b, cn, degree_a, count(DISTINCT nb) as degree_b
            WITH a, b, cn, degree_a, degree_b, (degree_a + degree_b - cn) AS union_size
            WITH a, b, cn, degree_a, degree_b,
                 CASE WHEN union_size > 0 THEN (cn * 1.0) / union_size ELSE 0.0 END AS jaccard,
                 (degree_a * degree_b) AS pref_attachment
            RETURN b.id AS target_id, b.name AS target_name, b.entity_type AS target_type,
                   cn AS common_neighbors, jaccard, pref_attachment
            ORDER BY cn DESC, jaccard DESC
            LIMIT $limit
            """
            
            results = session.run(query, entity_id=entity_id, limit=limit)
            
            # Find the max preferent attachment in this local result set to normalize it
            # PA grows very fast, so local normalization [0, 1] is best for composite scoring.
            records = [dict(r) for r in results]
            if not records:
                return {
                    "status": "no_structural_candidates",
                    "potential_links": [],
                    "reason": "No entities share sufficient structural similarity."
                }
                
            max_pa = max([r["pref_attachment"] for r in records]) if records else 1
            if max_pa == 0:
                max_pa = 1
                
            for record in records:
                cn = record["common_neighbors"]
                jaccard = record["jaccard"]
                raw_pa = record["pref_attachment"]
                
                # Normalize PA
                norm_pa = raw_pa / max_pa
                
                # Calculate Composite Score (must be [0, 1])
                # cn normalization: we'll say 10 common neighbors is a "perfect" score of 1.0 for this component.
                norm_cn = min(1.0, cn / 10.0)
                
                # Weighting: 40% CN, 40% Jaccard, 20% PA
                score = (0.40 * norm_cn) + (0.40 * jaccard) + (0.20 * norm_pa)
                score = round(score, 3)
                
                if score >= min_score:
                    explanations = []
                    explanations.append(f"The candidate shares {cn} common neighbors with the focal entity")
                    
                    if jaccard > 0.3:
                        explanations.append(f"and has overlapping local topology ({int(jaccard*100)}%).")
                    else:
                        explanations.append(".")
                        
                    potential_links.append({
                        "source_entity_id": entity_id,
                        "target_entity_id": record["target_id"],
                        "target_entity_name": record.get("target_name") or record["target_id"],
                        "target_entity_type": record.get("target_type") or "Unknown",
                        "score": score,
                        "signals": {
                            "common_neighbors": cn,
                            "jaccard_similarity": round(jaccard, 3),
                            "preferential_attachment_normalized": round(norm_pa, 3)
                        },
                        "weights": {
                            "common_neighbors": 0.40,
                            "jaccard": 0.40,
                            "preferential_attachment": 0.20
                        },
                        "explanation": {
                            "reason": " ".join(explanations),
                            "method": "common_neighbors + jaccard + preferential_attachment"
                        }
                    })
                    
        # Sort by final score descending
        potential_links.sort(key=lambda x: x["score"], reverse=True)

        return {
            "status": "success",
            "potential_links": potential_links,
            "reason": None
        }

neo4j_predictions = Neo4jPotentialLinkService()
