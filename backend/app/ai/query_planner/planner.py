import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.crime import Crime, CrimeType
from app.models.location import District, PoliceStation
from app.models.entities import Suspect, Vehicle
from app.ai.neo4j.intelligence import neo4j_intelligence
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class QueryPlanner:
    """Maps extracted intents to PostgreSQL queries and returns structured context."""

    @staticmethod
    def execute_intent(db: Session, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        intent = intent_data.get("intent", "general")
        crime_type = intent_data.get("crime_type")
        district = intent_data.get("district")

        handler_map = {
            "crime_search": QueryPlanner._crime_search,
            "suspect_search": QueryPlanner._suspect_search,
            "vehicle_search": QueryPlanner._vehicle_search,
            "station_search": QueryPlanner._station_search,
            "trends": QueryPlanner._trends,
            "hotspots": QueryPlanner._hotspots,
            "suspect_network": QueryPlanner._suspect_network,
            "vehicle_network": QueryPlanner._vehicle_network,
            "crime_network": QueryPlanner._crime_network,
            "repeat_offenders": QueryPlanner._repeat_offenders,
            "criminal_cluster": QueryPlanner._criminal_cluster,
            "general": QueryPlanner._general_stats,
        }

        handler = handler_map.get(intent, QueryPlanner._general_stats)
        try:
            data = handler(db, crime_type=crime_type, district=district)
        except Exception as e:
            logger.error(f"QueryPlanner failed for intent '{intent}': {e}")
            data = []

        return {
            "mapped_action": intent,
            "data": data,
            "record_count": len(data),
        }

    # ─── Crime Search ────────────────────────────────────────────
    @staticmethod
    def _crime_search(db: Session, **kwargs) -> List[Dict]:
        crime_type = kwargs.get("crime_type")
        district = kwargs.get("district")

        query = db.query(Crime).join(CrimeType).join(District)
        if crime_type:
            query = query.filter(CrimeType.name.ilike(f"%{crime_type}%"))
        if district:
            query = query.filter(District.district_name.ilike(f"%{district}%"))

        records = query.order_by(Crime.occurrence_date.desc()).limit(10).all()
        return [
            {
                "fir_number": r.fir_number,
                "title": r.title,
                "status": r.status,
                "crime_type": r.crime_type.name if r.crime_type else "Unknown",
                "district": r.district.district_name if r.district else "Unknown",
                "station": r.station.station_name if r.station else "Unknown",
                "date": r.occurrence_date.isoformat() if r.occurrence_date else "Unknown",
            }
            for r in records
        ]

    # ─── Suspect Search ──────────────────────────────────────────
    @staticmethod
    def _suspect_search(db: Session, **kwargs) -> List[Dict]:
        query = db.query(Suspect).order_by(Suspect.risk_score.desc()).limit(10)
        records = query.all()
        return [
            {
                "name": r.full_name,
                "alias": r.alias_name or "—",
                "gender": r.gender or "—",
                "age": r.age,
                "risk_score": float(r.risk_score) if r.risk_score else 0.0,
                "linked_cases": len(r.crimes) if r.crimes else 0,
            }
            for r in records
        ]

    # ─── Vehicle Search ──────────────────────────────────────────
    @staticmethod
    def _vehicle_search(db: Session, **kwargs) -> List[Dict]:
        records = db.query(Vehicle).limit(10).all()
        return [
            {
                "registration": r.registration_number,
                "type": r.vehicle_type or "—",
                "manufacturer": r.manufacturer or "—",
                "model": r.model or "—",
                "owner": r.owner_name or "—",
            }
            for r in records
        ]

    # ─── Station Search ──────────────────────────────────────────
    @staticmethod
    def _station_search(db: Session, **kwargs) -> List[Dict]:
        district = kwargs.get("district")
        query = db.query(PoliceStation).join(District)
        if district:
            query = query.filter(District.district_name.ilike(f"%{district}%"))
        records = query.limit(10).all()
        return [
            {
                "station_name": r.station_name,
                "station_code": r.station_code,
                "district": r.district.district_name if r.district else "Unknown",
                "address": r.address or "—",
            }
            for r in records
        ]

    # ─── Trends (Crime counts by type) ───────────────────────────
    @staticmethod
    def _trends(db: Session, **kwargs) -> List[Dict]:
        district = kwargs.get("district")
        query = (
            db.query(CrimeType.name, func.count(Crime.id).label("count"))
            .join(Crime, Crime.crime_type_id == CrimeType.id)
            .join(District, Crime.district_id == District.id)
        )
        if district:
            query = query.filter(District.district_name.ilike(f"%{district}%"))
        rows = query.group_by(CrimeType.name).order_by(desc("count")).limit(10).all()
        return [{"crime_type": row[0], "count": row[1]} for row in rows]

    # ─── Hotspots (Crime counts by district) ─────────────────────
    @staticmethod
    def _hotspots(db: Session, **kwargs) -> List[Dict]:
        rows = (
            db.query(District.district_name, func.count(Crime.id).label("count"))
            .join(Crime, Crime.district_id == District.id)
            .group_by(District.district_name)
            .order_by(desc("count"))
            .limit(10)
            .all()
        )
        return [{"district": row[0], "count": row[1]} for row in rows]

    # ─── Graph Networks (Neo4j) ──────────────────────────────────
    @staticmethod
    def _suspect_network(db: Session, **kwargs) -> List[Dict]:
        suspect_id = kwargs.get("suspect_id") or "S123" # Dummy fallback
        data = neo4j_intelligence.get_suspect_network(suspect_id)
        return data.get("nodes", [])

    @staticmethod
    def _vehicle_network(db: Session, **kwargs) -> List[Dict]:
        vehicle_num = kwargs.get("vehicle_number") or "KA01AB1234"
        return neo4j_intelligence.find_crimes_by_vehicle(vehicle_num)

    @staticmethod
    def _crime_network(db: Session, **kwargs) -> List[Dict]:
        fir = kwargs.get("fir_number") or "FIR-2025-441"
        data = neo4j_intelligence.execute_query(
            "MATCH path = (c:Crime {fir_number: $fir})-[*1..2]-(connected) UNWIND nodes(path) AS n RETURN collect(distinct n) AS nodes",
            parameters={"fir": fir}
        )
        if not data:
            return []
        nodes = data[0].get("nodes", [])
        return [{"id": n.element_id, "labels": list(n.labels), "props": dict(n)} for n in nodes]

    @staticmethod
    def _repeat_offenders(db: Session, **kwargs) -> List[Dict]:
        return neo4j_intelligence.find_repeat_offenders(10)

    @staticmethod
    def _criminal_cluster(db: Session, **kwargs) -> List[Dict]:
        data = neo4j_intelligence.get_high_risk_network()
        return data.get("nodes", [])

    # ─── General Stats ───────────────────────────────────────────
    @staticmethod
    def _general_stats(db: Session, **kwargs) -> List[Dict]:
        total_crimes = db.query(func.count(Crime.id)).scalar() or 0
        total_suspects = db.query(func.count(Suspect.id)).scalar() or 0
        total_stations = db.query(func.count(PoliceStation.id)).scalar() or 0
        total_districts = db.query(func.count(District.id)).scalar() or 0
        return [
            {
                "metric": "Total Crimes",
                "value": total_crimes,
            },
            {
                "metric": "Total Suspects",
                "value": total_suspects,
            },
            {
                "metric": "Police Stations",
                "value": total_stations,
            },
            {
                "metric": "Districts",
                "value": total_districts,
            },
        ]
