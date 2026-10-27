import unittest
import json
import os
import io
import sys

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from extensions import db
from models.user import User
from models.student import Student
from models.college import College

class TestApiEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

    def test_01_health_endpoint(self):
        """Test GET /api/health"""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "Authentication Validator API")

    def test_02_root_endpoint(self):
        """Test GET /"""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "ok")

    def test_03_auth_login_student(self):
        """Test POST /api/auth/login for demo student"""
        res = self.client.post(
            "/api/auth/login",
            data=json.dumps({"email": "rahul.patil@student.in", "password": "Password@123", "role": "student"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("token", data)
        self.assertEqual(data["user"]["role"], "student")

    def test_04_auth_login_college(self):
        """Test POST /api/auth/login for demo college"""
        res = self.client.post(
            "/api/auth/login",
            data=json.dumps({"email": "admin@nit.edu.in", "password": "Password@123", "role": "college"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("token", data)
        self.assertEqual(data["user"]["role"], "college")

    def test_05_public_college_qr_lookup(self):
        """Test GET /api/college/public-info/<identifier>"""
        res = self.client.get("/api/college/public-info/NIT101")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("college", data)
        self.assertEqual(data["college"]["college_id"], "NIT101")

if __name__ == "__main__":
    unittest.main()
