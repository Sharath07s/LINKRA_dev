import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.ai.neo4j.analytics import neo4j_analytics
from app.ai.neo4j.predictions import neo4j_predictions
from app.ai.neo4j.anomaly import neo4j_anomaly

def run():
    print("\n--- 1. Degree Centrality ---")
    deg = neo4j_analytics.get_degree_centrality(limit=5)
    print(deg)
    
    # Extract real IDs
    jane_id = next((x['entity_id'] for x in deg if 'jane smith' in x['name'].lower()), None)
    john_id = next((x['entity_id'] for x in deg if 'john doe' in x['name'].lower()), None)
    gang_id = next((x['entity_id'] for x in deg if 'gang' in x['name'].lower()), None)
    
    print(f"IDs - John: {john_id}, Jane: {jane_id}, Gang: {gang_id}")
    
    print("\n--- 2. Shortest Path ---")
    if john_id and gang_id:
        sp = neo4j_analytics.get_shortest_path(john_id, gang_id)
        print(sp)
        
    print("\n--- 3. Common Neighbors & Link Prediction ---")
    if john_id:
        preds = neo4j_predictions.get_potential_links_for_entity(john_id)
        print(f"Link Predictions for John Doe: {preds}")
            
    print("\n--- 4. Local Component Approximation ---")
    if john_id:
        comp = neo4j_analytics.get_local_component(john_id)
        print(f"Component Size (John Doe): {comp}")
        
    print("\n--- 5. Structural Anomaly Detection ---")
    anoms = neo4j_anomaly.get_top_anomalies(limit=5)
    print("Top Anomalies:")
    print(anoms)
    
run()
