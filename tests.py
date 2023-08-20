import unittest
from datetime import datetime, timedelta
from flask_simple_captcha import CAPTCHA, DEFAULT_CONFIG


class TestCAPTCHA(unittest.TestCase):
    def setUp(self):
        self.captcha = CAPTCHA(DEFAULT_CONFIG)

    def test_create(self):
        result = self.captcha.create()
        self.assertIn('img', result)
        self.assertIn('text', result)
        self.assertIn('hash', result)
        self.assertIn('id', result)
        self.assertEqual(len(result['text']), DEFAULT_CONFIG['CAPTCHA_LENGTH'])

    def test_verify_valid(self):
        captcha_data = self.captcha.create()
        c_text = captcha_data['text']
        c_hash = captcha_data['id']
        self.assertTrue(self.captcha.verify(c_text, c_hash))
        self.assertFalse(self.captcha.verify(c_text, c_hash))

    def test_verify_invalid(self):
        captcha_data = self.captcha.create()
        c_text = "WRONGTEXT"
        c_hash = captcha_data['id']
        self.assertFalse(self.captcha.verify(c_text, c_hash))

    def test_cleanup_old_hashes(self):
        # Add an old CAPTCHA entry
        c_hash = 'dummy_hash'
        timestamp = datetime.now() - timedelta(minutes=self.captcha.config['EXPIRE_MINUTES'] + 1)
        self.captcha.captchas[c_hash] = {'id': 'dummy_id', 'timestamp': timestamp}

        # Verify the old CAPTCHA entry is present
        self.assertIn(c_hash, self.captcha.captchas)

        # Run cleanup method
        self.captcha.cleanup_old_hashes()

        # Verify the old CAPTCHA entry has been removed
        self.assertNotIn(c_hash, self.captcha.captchas)

    def test_captcha_html(self):
        captcha_data = self.captcha.create()
        html = self.captcha.captcha_html(captcha_data)
        # Check if the returned value is a string containing HTML
        self.assertIsInstance(html, str)
        self.assertIn('<img', html)
        self.assertIn(
            '<input type="hidden" name="captcha-hash" value="%s">' % captcha_data['id'],
            html,
        )


if __name__ == '__main__':
    unittest.main()
