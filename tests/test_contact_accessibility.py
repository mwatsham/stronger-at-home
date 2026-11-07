from html.parser import HTMLParser
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ContactParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.controls = []
        self.appointment = False
        self.phone_near_form = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section':
            self.appointment = attrs.get('id') == 'appointment-request'
        if self.appointment and tag == 'a' and attrs.get('href') == 'tel:+447843497871':
            self.phone_near_form = True
        if tag in ('input', 'select'):
            self.controls.append(attrs.get('id'))


class ContactAccessibilityTests(unittest.TestCase):
    def test_rendered_form_explains_preference_before_contact_details(self):
        result = subprocess.run(['php', 'site/contact/index.php'], cwd=ROOT,
                                capture_output=True, text=True, check=True)
        parser = ContactParser(result.stdout)
        self.assertLess(parser.controls.index('preferred-contact'), parser.controls.index('email'))
        self.assertLess(parser.controls.index('preferred-contact'), parser.controls.index('phone'))
        self.assertTrue(parser.phone_near_form)

    def test_contact_requirement_behavior(self):
        result = subprocess.run(['node', 'tests/contact_requirements.cjs'], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
