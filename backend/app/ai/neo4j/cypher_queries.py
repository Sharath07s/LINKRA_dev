# backend/app/ai/neo4j/cypher_queries.py
"""
Cypher query constants.

All queries must be:
- Bounded (LIMIT applied or depth capped)
- Parameterized (no f-string variable interpolation of user input)
- Read-only where possible (no writes in query layer)
"""

# Default limits
DEFAULT_ASSOC_LIMIT = 50
DEFAULT_NETWORK_LIMIT = 150

FIND_ASSOCIATES = """
MATCH (e1:Entity {id: $entity_id})-[r1]-(c:Entity {entity_type: 'CRIME'})-[r2]-(associate:Entity)
WHERE e1.id <> associate.id AND associate.entity_type = 'PERSON'
RETURN associate.id AS associate_id, associate.name AS associate_name, count(c) AS shared_crimes
ORDER BY shared_crimes DESC
LIMIT $limit
"""

FIND_SHARED_VEHICLES = """
MATCH (e1:Entity {id: $entity_id})-[r1:OWNS|USES|CONNECTED_TO]-(v:Entity {entity_type: 'VEHICLE'})
      -[r2:OWNS|USES|CONNECTED_TO]-(associate:Entity)
WHERE e1.id <> associate.id AND associate.entity_type = 'PERSON'
RETURN associate.id AS associate_id, associate.name AS associate_name,
       v.name AS vehicle_number, count(v) AS weight
LIMIT $limit
"""

FIND_CRIMES_FOR_VEHICLE = """
MATCH (c:Entity {entity_type: 'CRIME'})-[r]-(v:Entity {name: $vehicle_number, entity_type: 'VEHICLE'})
RETURN c.id AS crime_id, c.name AS title
"""

# Fixed: previously returned `path` object which was unusable — now returns nodes/edges
FIND_CRIMINAL_NETWORK = """
MATCH (e:Entity {id: $entity_id})-[*1..2]-(connected:Entity)
WHERE e.id <> connected.id
WITH collect(distinct connected) AS connected_nodes
UNWIND connected_nodes AS n
OPTIONAL MATCH (e)-[r]-(n)
RETURN collect(distinct n) AS nodes, collect(distinct r) AS edges
"""

FIND_REPEAT_OFFENDERS = """
MATCH (s:Entity {entity_type: 'PERSON'})-[r]-(c:Entity {entity_type: 'CRIME'})
WITH s, count(c) AS crime_count
WHERE crime_count > 1
RETURN s.id AS suspect_id, s.name AS suspect_name, crime_count
ORDER BY crime_count DESC
LIMIT $limit
"""

FIND_MOST_CONNECTED_SUSPECTS = """
MATCH (s:Entity {entity_type: 'PERSON'})-[r]-()
RETURN s.id AS suspect_id, s.name AS suspect_name, count(r) AS connections
ORDER BY connections DESC
LIMIT $limit
"""

GET_NETWORK_NODES_EDGES = """
MATCH path = (e:Entity {id: $entity_id})-[*1..2]-(connected:Entity)
WITH path, connected LIMIT $limit
UNWIND nodes(path) AS n
UNWIND relationships(path) AS r
RETURN collect(distinct n) AS nodes, collect(distinct r) AS edges
"""

# Fixed: uses degree centrality to find highly connected nodes dynamically
GET_HIGH_RISK_NETWORK = """
MATCH (s:Entity)
WITH s, COUNT { (s)--() } AS degree
WHERE degree > 0
ORDER BY degree DESC
LIMIT $limit
MATCH path = (s)-[r]-(connected:Entity)
UNWIND nodes(path) AS n
UNWIND relationships(path) AS rel
RETURN collect(distinct n) AS nodes, collect(distinct rel) AS edges
"""

# Initialize Entity uniqueness constraint
ENSURE_ENTITY_CONSTRAINT = """
CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE
"""

# Get a single entity with its direct relationships
GET_ENTITY_WITH_RELATIONSHIPS = """
MATCH (e:Entity {id: $entity_id})
OPTIONAL MATCH (e)-[r]-(connected:Entity)
RETURN e AS entity, collect(distinct r) AS rels, collect(distinct connected) AS connected_nodes
"""
