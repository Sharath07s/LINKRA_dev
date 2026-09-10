"""
Investigate what connection_url the Aura API provides for our instance.
"""
import os
from dotenv import load_dotenv

def main():
    load_dotenv()

    client_id = os.getenv("AURA_CLIENT_ID")
    client_secret = os.getenv("AURA_CLIENT_SECRET")

    from graphdatascience.session.aura_api import AuraApi

    aura_api = AuraApi(
        aura_env=None,
        client_id=client_id,
        client_secret=client_secret,
        project_id=None,
    )

    # Get instance details
    instance = aura_api.list_instance("f725a8a2")
    if instance:
        print(f"Instance found: {instance.id}")
        print(f"  Name: {instance.name}")
        print(f"  Connection URL: {instance.connection_url}")
        print(f"  Status: {instance.status}")
        print(f"  Memory: {instance.memory}")
        print(f"  Type: {instance.type}")
        print(f"  Region: {instance.region}")
        print(f"  Cloud Provider: {instance.cloud_provider}")
    else:
        print("Instance NOT FOUND")

if __name__ == "__main__":
    main()
