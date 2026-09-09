import asyncio
from neo4j import AsyncGraphDatabase
from backend.app.core.config import settings

async def audit_neo4j():
    driver = AsyncGraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )
    async with driver.session() as session:
        try:
            # Nodes
            res = await session.run("MATCH (n) RETURN count(n) as node_count")
            nodes = (await res.single())["node_count"]
            print(f"Neo4j nodes: {nodes}")
            
            # Edges
            res = await session.run("MATCH ()-[r]->() RETURN count(r) as edge_count")
            edges = (await res.single())["edge_count"]
            print(f"Neo4j edges: {edges}")
            
            # Types
            res = await session.run("MATCH ()-[r]->() RETURN type(r) as t, count(r) as c")
            for record in await res.data():
                print(f"Rel type {record['t']}: {record['c']}")
                
        except Exception as e:
            print(f"Error: {e}")
    await driver.close()

if __name__ == "__main__":
    asyncio.run(audit_neo4j())
