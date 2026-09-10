"""
Test neo4j+s:// with SSL certificate debugging.
"""
import os
import ssl
import socket
from dotenv import load_dotenv

def main():
    load_dotenv()

    host = "f725a8a2.databases.neo4j.io"
    port = 7687

    print(f"Testing TLS to {host}:{port}")
    print(f"Python SSL version: {ssl.OPENSSL_VERSION}")

    # Test 1: Try standard SSL connection
    print("\n--- Test 1: Standard SSL verification ---")
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                print(f"  Connected with TLS {ssock.version()}")
                cert = ssock.getpeercert()
                print(f"  Subject: {cert.get('subject', 'N/A')}")
                print(f"  Issuer: {cert.get('issuer', 'N/A')}")
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}")

    # Test 2: Try without cert verification  
    print("\n--- Test 2: No cert verification ---")
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                print(f"  Connected with TLS {ssock.version()}")
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}")

    # Test 3: Try with neo4j driver + trusted_certificates=TRUST_ALL_CERTIFICATES
    print("\n--- Test 3: neo4j driver with TRUST_ALL ---")
    from neo4j import GraphDatabase, TrustAll
    neo4j_user = os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    try:
        driver = GraphDatabase.driver(
            f"neo4j+s://{host}",
            auth=(neo4j_user, neo4j_password),
            trusted_certificates=TrustAll(),
        )
        driver.verify_connectivity(database=neo4j_user)
        print(f"  PASS")
        
        with driver.session(database=neo4j_user) as session:
            cnt = session.run("MATCH (n) RETURN count(n) AS cnt").single()["cnt"]
            print(f"  Node count: {cnt}")
        driver.close()
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
