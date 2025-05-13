import unittest
from fastapi.testclient import TestClient
from main import app

class TestGeminiProxy(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "running", "service": "geminipy"})
    
    def test_missing_api_key(self):
        response = self.client.get("/v1/models")
        self.assertEqual(response.status_code, 401)
        self.assertIn("API 密钥缺失", response.json()["detail"])

if __name__ == "__main__":
    unittest.main() 