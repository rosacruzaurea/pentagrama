import unittest
import os
import subprocess
import sys
from content_search import validate_engine_id, content_security_policy


class SearchConfigTests(unittest.TestCase):
    def test_public_id_or_disabled_only(self):
        for value in ['', '0123456789:engine_1-x', 'a1b2c3']:
            self.assertEqual(validate_engine_id(value), value)
        for value in [None, 123, 'https://cse.google.com/test', '<script>', 'a b', 'a' * 101]:
            with self.assertRaises(ValueError):
                validate_engine_id(value)

    def test_script_policy_stays_restricted(self):
        disabled = content_security_policy()
        self.assertIn("script-src 'self';", disabled)
        self.assertIn("style-src 'self';", disabled)
        enabled = content_security_policy(True)
        script = enabled.split('script-src ')[1].split(';')[0]
        self.assertNotIn('unsafe-inline', script)
        self.assertNotIn('unsafe-eval', script)
        self.assertNotIn('*', script)
        self.assertIn('https://cse.google.com', script)
        self.assertNotIn('doubleclick', enabled)
        self.assertIn("object-src 'none'", enabled)
        self.assertIn("base-uri 'none'", enabled)

    def test_demo_cannot_build_for_production(self):
        env = {**os.environ, 'SEARCH_DEMO': '1', 'SITE_NOINDEX': '0'}
        result = subprocess.run([sys.executable, '-c', "import sys;sys.path.insert(0,'tools');import site_config"], env=env, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'SEARCH_DEMO requires SITE_NOINDEX=1', result.stderr)
