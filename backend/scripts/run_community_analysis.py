#!/usr/bin/env python3
import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_community_analysis():
    """
    Executes Louvain and Leiden community detection algorithms using GDS
    and writes the community IDs back to the Entity nodes in Neo4j as
    'louvain_community' and 'leiden_community' properties.
    """
    uri = settings.NEO4J_URI
    user = settings.NEO4J_USER
    password = settings.NEO4J_PASSWORD
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            logger.info("Dropping existing projection if any...")
            try:
                session.run("CALL gds.graph.drop('linkra_analysis_graph', false)")
            except Exception:
                pass
                
            logger.info("Projecting graph for community analysis...")
            session.run("""
                CALL gds.graph.project(
                    'linkra_analysis_graph',
                    'Entity',
                    {
                        _ALL_: {
                            type: '*',
                            orientation: 'UNDIRECTED'
                        }
                    }
                )
            """)
            
            logger.info("Executing Louvain algorithm and writing to graph...")
            louvain_res = session.run("""
                CALL gds.louvain.write('linkra_analysis_graph', {
                    writeProperty: 'louvain_community'
                })
                YIELD nodePropertiesWritten, computeMillis
                RETURN nodePropertiesWritten, computeMillis
            """).single()
            logger.info(f"Louvain completed in {louvain_res['computeMillis']}ms. Properties written: {louvain_res['nodePropertiesWritten']}")
            
            logger.info("Executing Leiden algorithm and writing to graph...")
            leiden_res = session.run("""
                CALL gds.leiden.write('linkra_analysis_graph', {
                    writeProperty: 'leiden_community'
                })
                YIELD nodePropertiesWritten, computeMillis
                RETURN nodePropertiesWritten, computeMillis
            """).single()
            logger.info(f"Leiden completed in {leiden_res['computeMillis']}ms. Properties written: {leiden_res['nodePropertiesWritten']}")
            
            logger.info("Dropping projection...")
            session.run("CALL gds.graph.drop('linkra_analysis_graph', false)")
            
            logger.info("Community analysis completed successfully.")
            
    except Exception as e:
        logger.error(f"Community analysis failed: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    run_community_analysis()
