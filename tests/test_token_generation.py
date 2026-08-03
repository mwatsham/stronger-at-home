import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.generate_brand_tokens import render_css
from scripts.validate_brand import validate_project


class TokenGenerationTests(unittest.TestCase):
    def test_render_css_is_deterministic_and_quotes_font_names(self):
        tokens = {
            "colour": {"brand": {"navy": "#203E55"}},
            "typography": {"family": {"body": "Atkinson Hyperlegible Next"}},
        }
        rendered = render_css(tokens)
        self.assertEqual(rendered, render_css(tokens))
        self.assertIn("--brand-colour-brand-navy: #203E55;", rendered)
        self.assertIn("--brand-typography-family-body: 'Atkinson Hyperlegible Next';", rendered)
        self.assertTrue(rendered.endswith("\n"))

    def test_generated_drift_is_reported(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "brand/generated").mkdir(parents=True)
            (root / "brand/tokens.json").write_text(
                '{"colour":{"brand":{"navy":"#203E55"}}}', encoding="utf-8"
            )
            (root / "brand/generated/tokens.css").write_text("stale", encoding="utf-8")
            errors = validate_project(root)
        self.assertIn("Generated token drift: brand/generated/tokens.css", errors)
