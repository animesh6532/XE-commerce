import unittest
import sys
import uuid
from pathlib import Path
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
APP_DIR = BACKEND_DIR / "app"

if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

try:
    from main import app
    MODULES_IMPORTED = True
except ImportError:
    MODULES_IMPORTED = False


class TestAuth(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if MODULES_IMPORTED:
            cls.client = TestClient(app)

    def setUp(self):
        self.assertTrue(MODULES_IMPORTED, "FastAPI app failed to import.")
        self.client = self.__class__.client
        self.test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.test_username = f"user_{uuid.uuid4().hex[:8]}"
        self.test_password = "securepassword123"

    def test_auth_workflow(self):
        # 1. Register a new user
        reg_payload = {
            "username": self.test_username,
            "email": self.test_email,
            "password": self.test_password
        }
        reg_response = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(reg_response.status_code, 201)
        reg_data = reg_response.json()
        self.assertEqual(reg_data["email"], self.test_email)
        self.assertEqual(reg_data["username"], self.test_username)

        # 2. Login
        login_payload = {
            "email": self.test_email,
            "password": self.test_password
        }
        login_response = self.client.post("/api/auth/login", json=login_payload)
        self.assertEqual(login_response.status_code, 200)
        login_data = login_response.json()
        self.assertIn("access_token", login_data)
        token = login_data["access_token"]

        # 3. Access /me (Protected)
        headers = {"Authorization": f"Bearer {token}"}
        me_response = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(me_response.status_code, 200)
        me_data = me_response.json()
        self.assertEqual(me_data["email"], self.test_email)

        # 4. Verify token
        verify_response = self.client.get("/api/auth/verify-token", headers=headers)
        self.assertEqual(verify_response.status_code, 200)
        self.assertTrue(verify_response.json()["valid"])

        # 5. Invalid Login
        bad_payload = {
            "email": self.test_email,
            "password": "wrongpassword"
        }
        bad_response = self.client.post("/api/auth/login", json=bad_payload)
        self.assertEqual(bad_response.status_code, 401)