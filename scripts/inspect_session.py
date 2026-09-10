import os
from dotenv import load_dotenv

def main():
    load_dotenv()

    client_id = os.getenv("AURA_CLIENT_ID")
    client_secret = os.getenv("AURA_CLIENT_SECRET")

    from graphdatascience import GdsSessions
    from graphdatascience.session import AuraAPICredentials

    credentials = AuraAPICredentials(client_id=client_id, client_secret=client_secret)
    sessions_mgr = GdsSessions(api_credentials=credentials)

    existing = sessions_mgr.list()
    for s in existing:
        print(f"Session: {s.name}")
        print(f"  ID: {s.id}")
        print(f"  Status: {s.status}")
        print(f"  Memory: {s.memory}")
        
        import inspect
        print("  Attributes:")
        for name, value in inspect.getmembers(s):
            if not name.startswith("_"):
                print(f"    {name}: {value}")

if __name__ == "__main__":
    main()
