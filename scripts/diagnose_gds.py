"""
Deep diagnostic of GDS session connection mechanism.
Inspects what the graphdatascience client is actually doing internally.
"""
import os
import logging
from dotenv import load_dotenv

# Enable DEBUG logging on neo4j driver to see exactly what's happening
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("neo4j").setLevel(logging.DEBUG)
logging.getLogger("graphdatascience").setLevel(logging.DEBUG)

def main():
    load_dotenv()

    client_id = os.getenv("AURA_CLIENT_ID")
    client_secret = os.getenv("AURA_CLIENT_SECRET")
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USER", os.getenv("NEO4J_USERNAME"))
    neo4j_password = os.getenv("NEO4J_PASSWORD")

    from graphdatascience import GdsSessions
    from graphdatascience.session import (
        AuraAPICredentials,
        DbmsConnectionInfo,
        SessionMemory,
    )

    credentials = AuraAPICredentials(client_id=client_id, client_secret=client_secret)
    sessions_mgr = GdsSessions(api_credentials=credentials)

    # List sessions and get details
    existing = sessions_mgr.list()
    print(f"\n{'='*60}")
    print(f"EXISTING SESSIONS: {len(existing)}")
    for s in existing:
        print(f"  Name: {s.name}")
        print(f"  ID: {s.id}")
        print(f"  Status: {s.status}")
        print(f"  Instance ID: {s.instance_id}")
        print(f"  Cloud Location: {s.cloud_location}")
        print(f"  Expiry: {s.expiry_date}")
        print(f"  Errors: {s.errors}")
    print(f"{'='*60}\n")

    # Now let's look at what the Aura API gives us for session details
    # The graphdatascience client must be getting connection info from somewhere
    import inspect
    
    # Inspect the GdsSessions class methods
    print("GdsSessions methods:")
    for name, method in inspect.getmembers(sessions_mgr, predicate=inspect.ismethod):
        if not name.startswith("_"):
            print(f"  {name}: {inspect.signature(method)}")

    # Look at the internal API client
    print(f"\nGdsSessions internal attributes:")
    for attr in dir(sessions_mgr):
        if not attr.startswith("__"):
            print(f"  {attr}")

    # Try to access the internal Aura API to get session connection details
    # The _api or similar attribute might have the session endpoint
    for attr in dir(sessions_mgr):
        if '_api' in attr.lower() or '_client' in attr.lower():
            val = getattr(sessions_mgr, attr, None)
            print(f"\n  {attr} = {val}")
            if val:
                for sub_attr in dir(val):
                    if not sub_attr.startswith("__"):
                        print(f"    {sub_attr}")

if __name__ == "__main__":
    main()
