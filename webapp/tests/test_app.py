from app import create_app
import unittest


class TestConfig:
    SLACK_SIGNING_SECRET = 'Test secret'
    SLACK_APP_TOKEN = 'Test app token'
    SLACK_BOT_TOKEN = 'Test bot token'


class AppTestCase(unittest.TestCase):

    def test_root_text(self):
        app = create_app()
        tester = app.test_client(self)
        response = tester.get('/')
        assert b'Hello world!' in response.data

    def test_slack_event_url_verification(self):
        app = create_app(TestConfig)
        tester = app.test_client(self)
        response = tester.post('/slack/event', json={
            'token': TestConfig.SLACK_SIGNING_SECRET,
            'type': 'url_verification',
            'challenge': 'This is the challenge text',
        })
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'This is the challenge text' == json_data['challenge']

    def test_slack_event_url_verification_auth_fail(self):
        app = create_app(TestConfig)
        tester = app.test_client(self)
        response = tester.post('/slack/event', json={
            'token': TestConfig.SLACK_SIGNING_SECRET + "BAD",
            'type': 'url_verification',
            'challenge': 'This is the challenge text',
        })
        assert response.status_code == 401
        json_data = response.get_json()
        assert json_data is None


if __name__ == '__main__':
    unittest.main()
