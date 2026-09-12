from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from app.core.config import settings
import logging
import time

logger = logging.getLogger(__name__)

class Neo4jConnection:
    def __init__(self):
        self.driver = None
        self.connect()

    def connect(self):
        if settings.NEO4J_URI:
            try:
                auth = (settings.NEO4J_USER, settings.NEO4J_PASSWORD) if (settings.NEO4J_USER and settings.NEO4J_PASSWORD) else None
                self.driver = GraphDatabase.driver(
                    settings.NEO4J_URI, 
                    auth=auth
                )
                self.driver.verify_connectivity()
                logger.info("Connected to Neo4j successfully.")
            except (ServiceUnavailable, AuthError, Exception) as e:
                logger.error(f"Failed to create Neo4j driver: {e}")
                self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def get_session(self):
        if not self.driver:
            self.connect()
        if self.driver:
            return self.driver.session()
        raise ServiceUnavailable("Neo4j database service is not available or not connected.")

    def check_health(self):
        if not self.driver:
            return {"status": "unhealthy", "reason": "Driver not initialized"}
        try:
            with self.driver.session() as session:
                result = session.run("CALL db.info()")
                info = result.single()
                
                # Fetch node and relationship counts
                counts_result = session.run("MATCH (n) RETURN count(n) as nodes")
                nodes = counts_result.single()["nodes"]
                
                rels_result = session.run("MATCH ()-[r]->() RETURN count(r) as relationships")
                rels = rels_result.single()["relationships"]
                
                return {
                    "status": "healthy",
                    "nodes": nodes,
                    "relationships": rels
                }
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return {"status": "unhealthy", "reason": str(e)}

neo4j_conn = Neo4jConnection()

def get_neo4j_session():
    session = neo4j_conn.get_session()
    if session:
        try:
            yield session
        finally:
            session.close()
    else:
        yield None
