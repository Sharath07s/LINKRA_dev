from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.entities import Suspect, SuspectCrime
from app.models.crime import Crime, CrimeType
from app.ai.neo4j.intelligence import neo4j_intelligence

class RecidivismEngine:
    def __init__(self, db: Session):
        self.db = db

    def predict_recidivism(self, suspect_id: str) -> dict:
        MIN_CRIMES = 2
        
        # 1. SQL Metrics
        suspect = self.db.query(Suspect).filter(Suspect.id == suspect_id).first()
        if not suspect:
            return {"status": "error", "message": "Suspect not found"}
            
        crimes_count = self.db.query(SuspectCrime).filter(SuspectCrime.suspect_id == suspect_id).count()
        
        if crimes_count < MIN_CRIMES:
            return {
                "status": "insufficient_data",
                "message": "Not enough criminal history for recidivism prediction.",
                "required_records": MIN_CRIMES,
                "available_records": crimes_count,
                "confidence": 0
            }
            
        # Analyze severity
        high_severity_crimes = self.db.query(SuspectCrime).join(Crime).join(CrimeType).filter(
            SuspectCrime.suspect_id == suspect_id,
            CrimeType.severity_level >= 4
        ).count()
        
        # 2. Neo4j Metrics
        cypher = "MATCH (s:Suspect {id: $suspect_id})-[:KNOWS]-(a:Suspect) RETURN count(a) as degree"
        degree_centrality = 0
        try:
            results = neo4j_intelligence.execute_query(cypher, parameters={"suspect_id": suspect_id})
            if results:
                degree_centrality = results[0]["degree"]
        except Exception:
            pass
            
        # 3. Calculate Risk Probability
        # Base probability from crime count
        probability = min(crimes_count * 0.15, 0.60)
        # Severity modifier
        probability += min(high_severity_crimes * 0.10, 0.20)
        # Network influence modifier
        probability += min(degree_centrality * 0.05, 0.15)
        
        probability = min(probability, 0.98) # Cap at 98%
        
        risk_level = "LOW"
        if probability >= 0.75:
            risk_level = "HIGH"
        elif probability >= 0.45:
            risk_level = "MEDIUM"
            
        evidence = [
            f"Historical crime count: {crimes_count}",
            f"High-severity crimes linked: {high_severity_crimes}",
            f"Neo4j network degree centrality: {degree_centrality}"
        ]
        
        return {
            "status": "success",
            "suspect_id": suspect_id,
            "probability": round(probability, 2),
            "risk_level": risk_level,
            "confidence": round(min(crimes_count * 0.2 + degree_centrality * 0.05, 0.9), 2),
            "evidence": evidence
        }
