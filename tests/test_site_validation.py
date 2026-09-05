from html.parser import HTMLParser
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

from scripts.validate_site import find_prohibited_content_categories, validate_site


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = {
    "site/index.html": "/",
    "site/about/index.html": "/about/",
    "site/how-i-can-help/index.html": "/how-i-can-help/",
    "site/appointments-and-fees/index.html": "/appointments-and-fees/",
    "site/contact/index.php": "/contact/",
}
BRANDED_PAGE_PATHS = (
    "site/index.html",
    "site/about/index.html",
    "site/how-i-can-help/index.html",
    "site/appointments-and-fees/index.html",
    "site/contact/index.php",
    "site/privacy/index.html",
    "site/accessibility/index.html",
    "site/404.html",
)


class LandmarkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.links, self.images, self.text, self.h1_count = (
            [],
            [],
            [],
            [],
            0,
        )

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.tags.append(tag)
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag == "img":
            self.images.append(attributes)
        if tag == "h1":
            self.h1_count += 1

    def handle_data(self, data):
        self.text.append(data)


class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms, self.controls = [], {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "form":
            self.forms.append(attributes)
        if tag in {"input", "select", "textarea"} and attributes.get("name"):
            self.controls[attributes["name"]] = attributes


class SiteValidationTests(unittest.TestCase):
    def test_every_public_page_uses_the_approved_compact_editorial_header(self):
        for relative_path in BRANDED_PAGE_PATHS:
            with self.subTest(relative_path=relative_path):
                html = (ROOT / relative_path).read_text(encoding="utf-8")
                header = html.split('<header class="site-header">', 1)[1].split(
                    "</header>", 1
                )[0]

                self.assertEqual(header.count('class="site-identity"'), 1)
                self.assertEqual(header.count('class="brand-home"'), 1)
                self.assertEqual(header.count('class="brand-strap"'), 1)
                self.assertEqual(header.count('class="site-navigation"'), 1)
                self.assertEqual(header.count("Home physiotherapy for adults"), 1)
                self.assertEqual(header.count("Epsom and surrounding areas"), 1)
                self.assertEqual(
                    header.count(
                        'aria-label="Stronger at Home Physiotherapy, home"'
                    ),
                    1,
                )
                self.assertEqual(
                    header.count(
                        'alt="Stronger at Home Physiotherapy by Melanie Watsham"'
                    ),
                    1,
                )
                self.assertLess(
                    header.index('class="site-identity"'),
                    header.index('class="site-navigation"'),
                )
                self.assertLess(
                    header.index('class="menu-button"'),
                    header.index('id="primary-navigation"'),
                )

    def test_compact_editorial_header_styles_preserve_logo_scale_and_link_affordance(self):
        stylesheet = (ROOT / "site/assets/css/site.css").read_text(encoding="utf-8")

        self.assertIn("background: #F9F4F2;", stylesheet)
        self.assertIn("width: min(100%, 19.6875rem);", stylesheet)
        self.assertIn(".brand-strap", stylesheet)
        self.assertIn(".site-navigation", stylesheet)
        self.assertIn("#primary-navigation a:not(.button):hover", stylesheet)
        self.assertIn("#primary-navigation a:not(.button):focus-visible", stylesheet)
        self.assertIn('#primary-navigation a[aria-current="page"]', stylesheet)
        self.assertIn("text-decoration: underline;", stylesheet)

    def test_primary_navigation_marks_the_current_page(self):
        for relative_path, route in PUBLIC_PAGES.items():
            with self.subTest(relative_path=relative_path):
                html = (ROOT / relative_path).read_text(encoding="utf-8")
                header = html.split('<header class="site-header">', 1)[1].split(
                    "</header>", 1
                )[0]
                self.assertIn(f'aria-current="page" href="{route}"', header)

    def test_policy_helper_does_not_flag_benign_registered_or_card_context(self):
        for text in (
            "Your enquiry is registered when submitted.",
            "This information card summarises the service.",
        ):
            with self.subTest(text=text):
                self.assertEqual(find_prohibited_content_categories(text), [])

    def test_development_site_has_no_structural_errors(self):
        self.assertEqual(validate_site(ROOT, "development"), [])

    def test_production_has_no_automated_publication_blockers(self):
        self.assertEqual(validate_site(ROOT, "production"), [])

    def test_privacy_notice_covers_legal_claims_transfers_and_required_fields(self):
        html = (ROOT / "site/privacy/index.html").read_text(encoding="utf-8")
        for required in (
            "Article 6(1)(c)",
            "Article 6(1)(f)",
            "Article 9(2)(f)",
            "UK-US Data Bridge",
            "UK International Data Transfer Agreement",
            "standard data protection clauses under Article 46(2)(c)",
            'id="privacy-objection"',
            "preferred contact method, postcode, short enquiry and privacy acknowledgement are required",
            "request more information or a copy of the relevant safeguards",
        ):
            with self.subTest(required=required):
                self.assertIn(required, html)

    def test_staging_is_not_indexable(self):
        text = (ROOT / "site/robots-staging.txt").read_text(encoding="utf-8")
        self.assertEqual(text, "User-agent: *\nDisallow: /\n")

    def test_validator_rejects_an_unknown_mode(self):
        with self.assertRaisesRegex(ValueError, "development, staging or production"):
            validate_site(ROOT, "preview")

    def test_validator_detects_broken_structure_metadata_and_local_links(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            path = copy / "site/about/index.html"
            html = path.read_text(encoding="utf-8")
            html = html.replace("<h1>About Melanie</h1>", "<h2>About Melanie</h2>")
            html = html.replace(
                '<meta property="og:title" content="About Melanie | Stronger at Home Physiotherapy">',
                "",
            )
            html = html.replace('href="/how-i-can-help/"', 'href="/missing/"', 1)
            path.write_text(html, encoding="utf-8")

            errors = validate_site(copy, "development")

            self.assertTrue(any("one h1" in error for error in errors), errors)
            self.assertTrue(any("og:title" in error for error in errors), errors)
            self.assertTrue(any("Missing local target" in error for error in errors), errors)

    def test_validator_detects_asset_and_form_accessibility_regressions(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            logo = copy / "site/assets/images/stronger-at-home-logo.png"
            logo.write_bytes(logo.read_bytes() + b"changed")
            contact = copy / "site/contact/index.php"
            html = contact.read_text(encoding="utf-8").replace(
                '<label for="postcode">Postcode <span aria-hidden="true">(required)</span></label>',
                '<span>Postcode <span aria-hidden="true">(required)</span></span>',
            )
            contact.write_text(html, encoding="utf-8")

            errors = validate_site(copy, "development")

            self.assertTrue(any("logo" in error.lower() for error in errors), errors)
            self.assertTrue(any("postcode" in error and "label" in error for error in errors), errors)

    def test_validator_rejects_unapproved_claims_and_structured_data_fields(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            home = copy / "site/index.html"
            html = home.read_text(encoding="utf-8")
            html = html.replace(
                "20+ years of NHS experience",
                "20+ years of NHS experience and guaranteed results",
                1,
            ).replace(
                '"areaServed":"Approximately 10 miles around Epsom, Surrey"',
                '"areaServed":"Approximately 10 miles around Epsom, Surrey","priceRange":"££"',
            )
            home.write_text(html, encoding="utf-8")

            errors = validate_site(copy, "development")

            self.assertTrue(any("Prohibited public content" in error for error in errors), errors)
            self.assertTrue(any("LocalBusiness fields" in error for error in errors), errors)

    def test_validator_rejects_transaction_method_wording(self):
        prohibited_examples = (
            "Payment details are available.",
            "Cash is accepted.",
            "Use a bank transfer.",
            "Bank details are provided.",
            "A sort code is provided.",
            "An account number is provided.",
            "Use a card.",
            "Use a cheque.",
            "Use a direct debit.",
            "Use BACS.",
            "Use PayPal.",
            "Use Apple Pay.",
            "Use Google Pay.",
            "An invoice is provided.",
            "Use a standing order.",
            "Pay by phone.",
            "We accept several methods.",
        )
        for example in prohibited_examples:
            with self.subTest(example=example), TemporaryDirectory() as directory:
                copy = Path(directory) / "project"
                shutil.copytree(ROOT, copy)
                home = copy / "site/index.html"
                html = home.read_text(encoding="utf-8").replace(
                    "</main>", f"<p>{example}</p></main>"
                )
                home.write_text(html, encoding="utf-8")

                errors = validate_site(copy, "development")

                self.assertIn(
                    "Public content approval drift: changed site/index.html",
                    errors,
                )

    def test_validator_rejects_registration_clinic_and_eligibility_claims(self):
        prohibited_examples = (
            "Registered physiotherapist.",
            "Stronger at Home®.",
            "Walk-in clinic.",
            "Eligibility criteria apply.",
            "Suitability is assessed.",
            "Exclusions apply.",
            "Service restrictions apply.",
            "We only treat people aged over 65.",
            "Patients must be referred.",
        )
        for example in prohibited_examples:
            with self.subTest(example=example), TemporaryDirectory() as directory:
                copy = Path(directory) / "project"
                shutil.copytree(ROOT, copy)
                home = copy / "site/index.html"
                html = home.read_text(encoding="utf-8").replace(
                    "</main>", f"<p>{example}</p></main>"
                )
                home.write_text(html, encoding="utf-8")

                errors = validate_site(copy, "development")

                self.assertIn(
                    "Public content approval drift: changed site/index.html",
                    errors,
                )

    def test_validator_checks_accessible_text_for_prohibited_content(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            home = copy / "site/index.html"
            html = home.read_text(encoding="utf-8").replace(
                'alt="Stronger at Home Physiotherapy by Melanie Watsham"',
                'alt="Payment details for Stronger at Home Physiotherapy"',
                1,
            )
            home.write_text(html, encoding="utf-8")

            errors = validate_site(copy, "development")

            self.assertTrue(
                any("Prohibited public content" in error for error in errors),
                errors,
            )

    def test_validator_rejects_a_bare_extra_service_location(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            home = copy / "site/index.html"
            html = home.read_text(encoding="utf-8").replace(
                "</main>", "<p>Leatherhead</p></main>"
            )
            home.write_text(html, encoding="utf-8")

            errors = validate_site(copy, "development")

            self.assertIn(
                "Public content approval drift: changed site/index.html",
                errors,
            )

    def test_reviewer_probes_require_public_content_reapproval(self):
        probes = (
            "Bitcoin accepted.",
            "Referral required.",
            "Drop-in appointments.",
            "Stronger at Home™.",
            "Richmond",
        )
        for probe in probes:
            with self.subTest(probe=probe), TemporaryDirectory() as directory:
                copy = Path(directory) / "project"
                shutil.copytree(ROOT, copy)
                home = copy / "site/index.html"
                html = home.read_text(encoding="utf-8").replace(
                    "</main>", f"<p>{probe}</p></main>"
                )
                home.write_text(html, encoding="utf-8")

                errors = validate_site(copy, "development")

                self.assertIn(
                    "Public content approval drift: changed site/index.html",
                    errors,
                )

    def test_public_content_approval_detects_added_removed_and_changed_sources(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            (copy / "site/new-page.html").write_text(
                "<!doctype html><title>New</title>\n", encoding="utf-8"
            )
            (copy / "site/robots-staging.txt").unlink()
            script = copy / "site/assets/js/site.js"
            script.write_text(script.read_text(encoding="utf-8") + "\n", encoding="utf-8")

            errors = validate_site(copy, "development")

            self.assertIn("Public content approval drift: added site/new-page.html", errors)
            self.assertIn("Public content approval drift: removed site/robots-staging.txt", errors)
            self.assertIn("Public content approval drift: changed site/assets/js/site.js", errors)

    def test_public_content_approval_detects_renamed_sources(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            old = copy / "site/robots-staging.txt"
            old.rename(copy / "site/robots-preview.txt")

            errors = validate_site(copy, "development")

            self.assertIn("Public content approval drift: added site/robots-preview.txt", errors)
            self.assertIn("Public content approval drift: removed site/robots-staging.txt", errors)

    def test_public_tree_approval_detects_files_regardless_of_name_or_extension(self):
        added_paths = (
            "site/public-data.json",
            "site/app.webmanifest",
            "site/page.htm",
            "site/NOTICE",
            "site/nested/portrait-copy.bmp",
        )
        for relative_path in added_paths:
            with self.subTest(relative_path=relative_path), TemporaryDirectory() as directory:
                copy = Path(directory) / "project"
                shutil.copytree(ROOT, copy)
                added = copy / relative_path
                added.parent.mkdir(parents=True, exist_ok=True)
                added.write_bytes(b"unapproved public file\n")

                errors = validate_site(copy, "development")

                self.assertIn(
                    f"Public content approval drift: added {relative_path}",
                    errors,
                )

    def test_public_tree_approval_rejects_symlinks(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            link = copy / "site/linked-file"
            link.symlink_to(copy / "site/robots.txt")

            errors = validate_site(copy, "development")

            self.assertIn("Public tree approval drift: symlink site/linked-file", errors)

    def test_public_tree_approval_rejects_added_empty_directories(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            (copy / "site/unapproved-directory").mkdir()

            errors = validate_site(copy, "development")

            self.assertIn(
                "Public tree approval drift: added directory site/unapproved-directory",
                errors,
            )

    def test_validator_requires_the_approved_contact_routes(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            contact = copy / "site/contact/index.php"
            html = contact.read_text(encoding="utf-8").replace(
                'href="tel:+447843497871"', 'href="/contact/"'
            )
            contact.write_text(html, encoding="utf-8")

            errors = validate_site(copy, "development")

            self.assertIn("Contact page must publish the approved phone and email routes", errors)

    def test_validator_requires_every_privacy_notice_section(self):
        required_sections = (
            "privacy-controller",
            "privacy-information",
            "privacy-lawful-basis",
            "privacy-sharing",
            "privacy-retention",
            "privacy-rights",
            "privacy-objection",
            "privacy-complaints",
        )
        for missing in required_sections:
            with self.subTest(missing=missing), TemporaryDirectory() as directory:
                copy = Path(directory) / "project"
                shutil.copytree(ROOT, copy)
                privacy = copy / "site/privacy/index.html"
                html = privacy.read_text(encoding="utf-8")
                target = f'id="{missing}"'
                self.assertIn(target, html)
                privacy.write_text(
                    html.replace(target, f'id="{missing}-removed"', 1),
                    encoding="utf-8",
                )

                errors = validate_site(copy, "development")

                self.assertIn(
                    f"Privacy notice is missing required section: {missing}",
                    errors,
                )

    def test_validator_allows_the_official_ico_complaints_link(self):
        errors = validate_site(ROOT, "development")

        self.assertFalse(
            any(error.startswith("External URL is not approved") for error in errors),
            errors,
        )

    def test_validator_still_rejects_other_external_links(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            privacy = copy / "site/privacy/index.html"
            html = privacy.read_text(encoding="utf-8").replace(
                "https://ico.org.uk/make-a-complaint/data-protection-complaints/check-if-you-can-complain/",
                "https://example.com/complaints/",
                1,
            )
            privacy.write_text(html, encoding="utf-8")

            errors = validate_site(copy, "development")

            self.assertIn(
                "External URL is not approved in site/privacy/index.html: https://example.com/complaints/",
                errors,
            )

    def test_validator_checks_sitemap_and_staging_crawl_policy(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            (copy / "site/sitemap.xml").write_text("<urlset></urlset>\n", encoding="utf-8")
            (copy / "site/robots-staging.txt").write_text(
                "User-agent: *\nAllow: /\n", encoding="utf-8"
            )

            errors = validate_site(copy, "staging")

            self.assertTrue(any("Sitemap routes" in error for error in errors), errors)
            self.assertIn("Staging robots policy must disallow all crawling", errors)

    def test_validator_rejects_reordered_server_directives(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            path = copy / "site/.htaccess"
            lines = path.read_text(encoding="utf-8").splitlines()
            lines[3], lines[4] = lines[4], lines[3]
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")

            errors = validate_site(copy, "development")

            self.assertIn("Server directives must exactly match the approved configuration", errors)

    def test_server_directives_allowlist_hosts_without_server_name_redirects(self):
        htaccess = (ROOT / "site/.htaccess").read_text(encoding="utf-8")

        self.assertNotIn("%{SERVER_NAME}", htaccess)
        self.assertIn("staging\\.stronger-at-home\\.co\\.uk", htaccess)
        self.assertIn("www\\.stronger-at-home\\.co\\.uk", htaccess)
        self.assertIn("[R=400,L]", htaccess)

    def test_validator_requires_public_font_license_copies(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            (copy / "site/assets/fonts/OFL-source-serif.txt").unlink()

            errors = validate_site(copy, "development")

            self.assertIn(
                "Public content approval drift: removed site/assets/fonts/OFL-source-serif.txt",
                errors,
            )

    def test_validator_rejects_conflicting_server_directives(self):
        conflicting_directives = (
            "Options +Indexes",
            "ErrorDocument 404 /other.html",
            "RewriteRule ^other$ / [R=302,L]",
            'Header unset Content-Security-Policy',
        )
        for directive in conflicting_directives:
            with self.subTest(directive=directive), TemporaryDirectory() as directory:
                copy = Path(directory) / "project"
                shutil.copytree(ROOT, copy)
                path = copy / "site/.htaccess"
                path.write_text(
                    path.read_text(encoding="utf-8") + directive + "\n",
                    encoding="utf-8",
                )

                errors = validate_site(copy, "development")

                self.assertIn(
                    "Server directives must exactly match the approved configuration",
                    errors,
                )

    def test_validator_rejects_nested_svg_logo_derivatives(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            derivative = copy / "site/assets/images/nested/logo-derived.svg"
            derivative.parent.mkdir()
            derivative.write_text("<svg xmlns=\"http://www.w3.org/2000/svg\"></svg>\n", encoding="utf-8")

            errors = validate_site(copy, "development")

            self.assertIn(
                "Public content approval drift: added site/assets/images/nested/logo-derived.svg",
                errors,
            )

    def test_validator_rejects_nested_raster_logo_derivatives(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            derivative = copy / "site/assets/images/nested/logo-derived.png"
            derivative.parent.mkdir()
            shutil.copyfile(
                copy / "site/assets/images/stronger-at-home-logo.png",
                derivative,
            )

            errors = validate_site(copy, "development")

            self.assertIn(
                "Public content approval drift: added site/assets/images/nested/logo-derived.png",
                errors,
            )

    def test_validator_rejects_top_level_public_logo_derivatives(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy)
            (copy / "site/logo-derived.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg"></svg>\n', encoding="utf-8"
            )

            errors = validate_site(copy, "development")

            self.assertIn(
                "Public content approval drift: added site/logo-derived.svg",
                errors,
            )

    def test_contact_form_collects_only_approved_fields(self):
        parser = FormParser()
        parser.feed((ROOT / "site/contact/index.php").read_text(encoding="utf-8"))

        self.assertEqual(parser.forms[0]["method"].lower(), "post")
        self.assertEqual(parser.forms[0]["action"], "/api/enquiry.php")
        self.assertEqual(
            set(parser.controls),
            {
                "name",
                "email",
                "phone",
                "preferred_contact",
                "postcode",
                "message",
                "privacy_acknowledged",
                "website",
                "csrf_token",
            },
        )
        self.assertNotIn("date_of_birth", parser.controls)
        self.assertNotIn("medical_history", parser.controls)

    def test_contact_form_requires_safe_fields_and_explains_the_booking_flow(self):
        html = (ROOT / "site/contact/index.php").read_text(encoding="utf-8")
        parser = FormParser()
        parser.feed(html)

        for field in ("name", "postcode", "message", "privacy_acknowledged"):
            self.assertIn("required", parser.controls[field], field)
        self.assertEqual(parser.controls["email"]["type"], "email")
        self.assertEqual(parser.controls["phone"]["type"], "tel")
        self.assertIn("Use this form to request an appointment.", html)
        self.assertIn("confirm availability", html)
        self.assertIn("Please do not include detailed or urgent medical information.", html)
        self.assertIn("+447843497871", html)
        self.assertIn("melanie@stronger-at-home.co.uk", html)
        for label in (
            "Name",
            "Email address",
            "Phone number",
            "Preferred contact method",
            "Postcode",
            "Short enquiry",
            "privacy notice",
        ):
            self.assertIn(label, html)
        self.assertIn('role="status"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertRegex(
            html,
            r'<textarea[^>]+name="message"[^>]*></textarea>',
        )

    def test_contact_form_uses_native_field_reporting_and_44px_privacy_targets(self):
        javascript = (ROOT / "site/assets/js/site.js").read_text(encoding="utf-8")
        stylesheet = (ROOT / "site/assets/css/site.css").read_text(encoding="utf-8")

        self.assertIn("preferredContact", javascript)
        self.assertIn("email.setCustomValidity", javascript)
        self.assertIn("phone.setCustomValidity", javascript)
        self.assertIn("form.reportValidity()", javascript)
        self.assertIn("Please check the highlighted fields", javascript)
        self.assertIn("status.textContent = '';", javascript)
        privacy_label = stylesheet.split(".form-field-checkbox label {", 1)[1].split("}", 1)[0]
        privacy_link = stylesheet.split(".form-field-checkbox a {", 1)[1].split("}", 1)[0]
        privacy_checkbox = stylesheet.split(".form-field-checkbox input {", 1)[1].split("}", 1)[0]
        self.assertIn("min-height: 44px;", privacy_label)
        self.assertIn("min-height: 44px;", privacy_link)
        self.assertIn("inline-size: 44px;", privacy_checkbox)
        self.assertIn("block-size: 44px;", privacy_checkbox)

    def test_homepage_uses_approved_patient_first_content_order(self):
        html = (ROOT / "site/index.html").read_text(encoding="utf-8")
        ids = [
            "introduction",
            "how-i-can-help",
            "benefits-at-home",
            "meet-melanie",
            "appointments",
            "area-and-fees",
            "request-an-appointment",
        ]

        section_ids = []
        for tag in html.split("<section ")[1:]:
            attributes = tag.split(">", 1)[0]
            if 'id="' in attributes:
                section_ids.append(attributes.split('id="', 1)[1].split('"', 1)[0])

        self.assertEqual(section_ids, ids)
        self.assertIn("Physiotherapy to help you feel stronger at home", html)
        self.assertIn("20+ years of NHS experience", html)

    def test_homepage_intro_uses_appointment_request_as_primary_action(self):
        html = (ROOT / "site/index.html").read_text(encoding="utf-8")
        introduction = html.split('<section id="introduction"', 1)[1].split(
            '<section id="how-i-can-help"', 1
        )[0]
        primary_action = '<a class="button" href="/contact/#appointment-request">Request an appointment</a>'
        secondary_action = '<a class="text-link" href="tel:+447843497871">Call Melanie</a>'

        self.assertIn(primary_action, introduction)
        self.assertIn(secondary_action, introduction)
        self.assertLess(introduction.index(primary_action), introduction.index(secondary_action))

    def test_homepage_claim_boundary_preserves_approved_facts_without_invented_claims(self):
        html = (ROOT / "site/index.html").read_text(encoding="utf-8")
        approved_facts = [
            "After surgery, a hospital admission or a fall",
            "falls prevention",
            "Appointments are arranged flexibly, subject to availability.",
            "Fees are quoted individually because travel requirements vary by location.",
            "A fixed price will be confirmed and agreed before the appointment is booked.",
        ]
        prohibited_claims = [
            "HCPC",
            "CSP",
            "AGILE",
            "ATOCP",
            "guaranteed",
            "testimonial",
            "review",
            "referral suitability",
            "referral exclusion",
            "emergency",
            "personal plan",
        ]

        for fact in approved_facts:
            self.assertIn(fact, html)
        for claim in prohibited_claims:
            self.assertNotIn(claim.lower(), html.lower(), claim)

    def test_homepage_uses_the_approved_web_portrait(self):
        portrait = ROOT / "site/assets/images/melanie-watsham-portrait.jpg"
        html = (ROOT / "site/index.html").read_text(encoding="utf-8")
        parser = LandmarkParser()
        parser.feed(html)

        self.assertTrue(portrait.is_file())
        with Image.open(portrait) as image:
            self.assertEqual(image.format, "JPEG")
            self.assertEqual(image.size, (1020, 1190))
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(len(image.getexif()), 0)

        matching_images = [
            image
            for image in parser.images
            if image.get("src") == "/assets/images/melanie-watsham-portrait.jpg"
        ]
        self.assertEqual(
            matching_images,
            [
                {
                    "src": "/assets/images/melanie-watsham-portrait.jpg",
                    "alt": "Melanie Watsham, physiotherapist",
                    "width": "1020",
                    "height": "1190",
                }
            ],
        )
        self.assertNotIn('data-production-blocker="portrait"', html)
        self.assertNotIn("Professional portrait to be supplied", html)

    def test_mobile_menu_is_a_javascript_enhancement_with_an_accurate_disclosure_control(self):
        stylesheet = (ROOT / "site/assets/css/site.css").read_text(encoding="utf-8")

        self.assertRegex(
            stylesheet,
            r"\.menu-button \{\n  display: none;",
        )
        self.assertRegex(
            stylesheet,
            r"\.js \.menu-button \{\n    display: block;",
        )
        self.assertRegex(
            stylesheet,
            r"\.js #primary-navigation \{ display: none;",
        )
        self.assertRegex(
            stylesheet,
            r'\.js #primary-navigation\[data-open="true"\] \{ display: flex; \}',
        )

    def test_focus_indicator_uses_the_high_contrast_two_colour_treatment(self):
        stylesheet = (ROOT / "site/assets/css/site.css").read_text(encoding="utf-8")

        self.assertIn(
            "outline: 3px solid var(--brand-colour-text-inverse);",
            stylesheet,
        )
        self.assertIn(
            "box-shadow: 0 0 0 6px var(--brand-colour-background-strong);",
            stylesheet,
        )
        self.assertNotIn(
            "outline: 3px solid var(--brand-colour-accent-progress);",
            stylesheet,
        )

    def test_every_primary_page_has_common_landmarks_and_one_h1(self):
        for relative_path in PUBLIC_PAGES:
            parser = LandmarkParser()
            parser.feed((ROOT / relative_path).read_text(encoding="utf-8"))
            self.assertTrue({"header", "nav", "main", "footer"}.issubset(parser.tags))
            self.assertEqual(parser.h1_count, 1, relative_path)

    def test_every_page_links_all_primary_routes_and_appointment_action(self):
        expected = set(PUBLIC_PAGES.values()) | {"/contact/#appointment-request"}
        for relative_path in PUBLIC_PAGES:
            parser = LandmarkParser()
            parser.feed((ROOT / relative_path).read_text(encoding="utf-8"))
            self.assertTrue(expected.issubset(set(parser.links)), relative_path)

    def test_information_pages_present_approved_service_and_appointment_facts(self):
        about = (ROOT / "site/about/index.html").read_text(encoding="utf-8")
        help_page = (ROOT / "site/how-i-can-help/index.html").read_text(encoding="utf-8")
        appointments = (ROOT / "site/appointments-and-fees/index.html").read_text(
            encoding="utf-8"
        )

        self.assertIn("20+ years of NHS experience", about)
        for phrase in (
            "Recovery after surgery",
            "Following a hospital admission",
            "A decline in mobility or physical function",
            "Rehabilitation following a fall",
            "Falls prevention",
            "Mobility and balance",
        ):
            self.assertIn(phrase, help_page)
        for phrase in (
            "60 minutes",
            "45 minutes",
            "approximately 10 miles of Epsom",
            "subject to availability",
            "postcode or address",
            "A fixed price will be confirmed and agreed before the appointment is booked.",
        ):
            self.assertIn(phrase, appointments)

    def test_information_pages_use_clear_page_titles_as_their_top_level_headings(self):
        expected_headings = {
            "site/about/index.html": "About Melanie",
            "site/how-i-can-help/index.html": "How I can help",
            "site/appointments-and-fees/index.html": "Appointments and fees",
        }

        for relative_path, heading in expected_headings.items():
            html = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn(f"<h1>{heading}</h1>", html)

    def test_public_pages_omit_unapproved_claims(self):
        visible_text = []
        for path in PUBLIC_PAGES:
            parser = LandmarkParser()
            parser.feed((ROOT / path).read_text(encoding="utf-8"))
            visible_text.extend(parser.text)
        combined = " ".join(visible_text).lower()

        for text in (
            "hcpc",
            "csp",
            "agile",
            "atocp",
            "guaranteed",
            "walk-in clinic",
            "testimonial",
            "review",
            "emergency",
        ):
            self.assertNotIn(text, combined)
