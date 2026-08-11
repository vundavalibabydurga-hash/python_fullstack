import os
import sqlite3
import unittest

from app import app


class SqliteIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'users.db')
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_registration_and_login_persist_in_sqlite(self):
        client = app.test_client()

        payload = {
            'name': 'Alice',
            'email': 'alice@example.com',
            'password': 'secret123',
            'dob': '2000-01-01',
            'gender': 'female',
            'course': 'Python FullStack'
        }

        response = client.post('/api/register', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'success')

        conn = sqlite3.connect(self.db_path)
        row = conn.execute(
            'SELECT email, password FROM users WHERE email = ?',
            ('alice@example.com',)
        ).fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], 'alice@example.com')
        self.assertEqual(row[1], 'secret123')

        login_response = client.post('/api/login', json={
            'email': 'alice@example.com',
            'password': 'secret123'
        })
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.get_json()['status'], 'success')


if __name__ == '__main__':
    unittest.main()
