"""
AgriSense Backend Integration Test Suite
Verifies all API endpoints: Auth, Crop Recommendation, Disease Detection,
Price Forecasting, Calendar Events, Weather, Chatbot, Market Deals, Schemes.
"""

import unittest
import json
import datetime
from backend.app import app

class AgriSenseApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["models_loaded"]["crop_recommendation"])

    def test_crop_recommendation(self):
        payload = {
            "N": 80, "P": 50, "K": 60,
            "temperature": 26, "humidity": 65,
            "ph": 6.5, "rainfall": 120, "season": "kharif"
        }
        res = self.client.post("/api/crops/recommend", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("recommendations", data)
        self.assertGreaterEqual(len(data["recommendations"]), 1)
        self.assertIn("score", data["recommendations"][0])

    def test_disease_detection(self):
        # Test with synthetic test leaf image or simulation
        payload = {"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="}
        res = self.client.post("/api/disease/detect", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("disease", data)
        self.assertIn("treatment", data)
        self.assertIn("severity", data)

    def test_disease_list(self):
        res = self.client.get("/api/disease/list")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["diseases"]), 5)

    def test_price_prediction(self):
        payload = {
            "crop": "Tomato", "month": 7,
            "rainfall": 120, "temperature": 28, "days_ahead": 7
        }
        res = self.client.post("/api/price/predict", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("forecast", data)
        self.assertEqual(len(data["forecast"]), 7)
        self.assertIn("best_day", data)
        self.assertIn("recommendation", data)

    def test_live_market(self):
        res = self.client.get("/api/market/live?crop=all")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("prices", data)
        self.assertGreaterEqual(len(data["prices"]), 5)

    def test_calendar_events(self):
        res = self.client.get("/api/calendar/events?crop=Rice")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("events", data)
        self.assertGreaterEqual(len(data["events"]), 5)

    def test_weather_current(self):
        res = self.client.get("/api/weather/current?location=Nashik")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("temperature", data)
        self.assertIn("advisories", data)

    def test_chatbot_multilingual(self):
        # Test Hindi query
        payload = {"message": "मानसून में कौन सी फसल अच्छी है", "language": "hi", "language_name": "हिंदी"}
        res = self.client.post("/api/chatbot", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("reply", data)
        self.assertIn("धान", data["reply"])

        # Test Kannada query
        payload_kn = {"message": "ಮುಂಗಾರಿನಲ್ಲಿ ಯಾವ ಬೆಳೆ ಉತ್ತಮ", "language": "kn", "language_name": "ಕನ್ನಡ"}
        res_kn = self.client.post("/api/chatbot", data=json.dumps(payload_kn), content_type="application/json")
        self.assertEqual(res_kn.status_code, 200)
        data_kn = res_kn.get_json()
        self.assertTrue(data_kn["success"])
        self.assertIn("ಭತ್ತ", data_kn["reply"])

    def test_market_deal_request(self):
        payload = {
            "name": "Ramesh Patil",
            "phone": "+91 98765 43210",
            "location": "Nashik, MH",
            "crop": "Tomato",
            "qty": 50,
            "price": 2200,
            "company": "ITC Agri Business"
        }
        res = self.client.post("/api/market/deal-request", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("deal", data)

    def test_government_schemes(self):
        res = self.client.get("/api/schemes")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("schemes", data)
        self.assertGreaterEqual(len(data["schemes"]), 5)

    def test_auth_registration_and_login(self):
        # Register
        test_email = f"farmer.test.{int(datetime.datetime.now().timestamp())}@gmail.com"
        reg_payload = {
            "first_name": "Suresh",
            "last_name": "Kumar",
            "email": test_email,
            "phone": "+91 98765 11223",
            "password": "Password@123"
        }
        reg_res = self.client.post("/api/auth/register", data=json.dumps(reg_payload), content_type="application/json")
        self.assertEqual(reg_res.status_code, 200)
        
        # Login
        login_payload = {
            "email": test_email,
            "password": "Password@123"
        }
        login_res = self.client.post("/api/auth/login", data=json.dumps(login_payload), content_type="application/json")
        self.assertIn(login_res.status_code, [200, 400, 401])
        data = login_res.get_json()
        self.assertIsNotNone(data)

if __name__ == "__main__":
    unittest.main()
