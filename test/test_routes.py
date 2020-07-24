import unittest
from app import app, db


class RoutesTestCase(unittest.TestCase):

    def test_version(self):

        test_client = app.test_client()
        response = test_client.get('/qiskit-service/api/v1.0/version')

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue("version" in json_data)
        self.assertEqual(json_data['version'], "1.0")

if __name__ == "__main__":
    unittest.main()