import os
from dotenv import load_dotenv
from graphdatascience import GraphDataScience

def main():
    load_dotenv()
    
    neo4j_uri = os.getenv("NEO4J_URI")  # should be neo4j+ssc://...
    neo4j_user = os.getenv("NEO4J_USER", os.getenv("NEO4J_USERNAME"))
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    print(f"Connecting to {neo4j_uri}...")
    
    try:
        gds = GraphDataScience(
            neo4j_uri.replace("neo4j+ssc://", "neo4j+s://"),
            auth=(neo4j_user, neo4j_password),
            database=neo4j_user,
            aura_ds=True
        )
        print("GDS Client initialization: PASS")
        
    except Exception as e:
        print(f"GDS Client initialization: FAILED ({type(e).__name__}: {e})")

if __name__ == "__main__":
    main()
