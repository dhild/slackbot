from app import app
import os

import unittest


class AppTestCase(unittest.TestCase):

    def test_root_text(self):
        tester = app.test_client(self)
        response = tester.get('/')
        assert b'Hello world!' in response.data

    def test_slack_event_url_verification(self):
        tester = app.test_client(self)
        response = tester.post('/slack/event', json={
            'token': os.environ.get('SLACK_VERIFICATION_TOKEN'),
            'type': 'url_verification',
            'challenge': 'This is the challenge text',
        })
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'This is the challenge text' == json_data['challenge']

    def test_slack_event_url_verification_auth_fail(self):
        tester = app.test_client(self)
        response = tester.post('/slack/event', json={
            'token': 'BAD TOKEN',
            'type': 'url_verification',
            'challenge': 'This is the challenge text',
        })
        assert response.status_code == 401
        json_data = response.get_json()
        assert json_data is None


if __name__ == '__main__':
    unittest.main()
