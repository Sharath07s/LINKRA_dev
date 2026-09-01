import sys
import logging
import sys
import logging
from fastapi.testclient import TestClient
from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = TestClient(app)
API_URL = "/api/v1"

def test_login():
    try:
        response = client.post(
            f"{API_URL}/auth/login",
            data={"username": "DEV-ADMIN", "password": "admin"}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            logger.info("Login successful. JWT generated.")
            return token
        else:
            logger.error(f"Login failed: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return None

def test_protected_route(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(
            f"{API_URL}/users/me",
            headers=headers
        )
        if response.status_code == 200:
            logger.info(f"Protected route accessed successfully: {response.json().get('email')}")
            return True
        else:
            logger.error(f"Protected route failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error during protected route test: {e}")
        return False

if __name__ == "__main__":
    token = test_login()
    if token:
        test_protected_route(token)
    else:
        sys.exit(1)
