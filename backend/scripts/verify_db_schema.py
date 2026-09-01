import sys
import os
from sqlalchemy import inspect
from app.db.session import engine

def verify_schema():
    print("Verifying PostgreSQL Schema...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    expected_tables = {
        'users', 'roles', 'permissions', 'role_permissions',
        'districts', 'police_stations',
        'crimes', 'crime_types', 'crime_status_history',
        'suspects', 'suspect_crimes', 'victims', 'victim_crimes',
        'vehicles', 'crime_vehicles',
        'evidence', 'investigations', 'investigation_notes',
        'reports', 'ai_conversations', 'ai_messages', 'ai_query_logs',
        'crime_predictions', 'hotspot_analysis', 'audit_logs', 'notifications'
    }
    
    missing_tables = expected_tables - set(tables)
    if missing_tables:
        print(f"FAILED: Missing tables: {missing_tables}")
    else:
        print("SUCCESS: All expected tables are present.")
        
    # Check some essential columns
    if 'users' in tables:
        columns = [c['name'] for c in inspector.get_columns('users')]
        if 'email' in columns and 'password_hash' in columns and 'role_id' in columns:
            print("SUCCESS: Users table has correct security columns.")
        else:
            print("FAILED: Users table is missing security columns.")
            
if __name__ == "__main__":
    try:
        verify_schema()
    except Exception as e:
        print(f"Error during schema verification: {e}")
