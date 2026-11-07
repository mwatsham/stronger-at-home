from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LinksAndTargets(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.ids = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            self.links.append(attrs.get('href'))
        if 'id' in attrs:
            self.ids.append(attrs['id'])


class RespiratoryNavigationTests(unittest.TestCase):
    def test_respiratory_card_leads_to_unique_service_section(self):
        home = LinksAndTargets((ROOT / 'site/index.html').read_text())
        service = LinksAndTargets((ROOT / 'site/how-i-can-help/index.html').read_text())
        self.assertIn('/how-i-can-help/#respiratory-physiotherapy', home.links)
        self.assertEqual(service.ids.count('respiratory-physiotherapy'), 1)
