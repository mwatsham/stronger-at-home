#!/usr/bin/env python3
"""Validate the public website without making network requests."""

from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
import posixpath
from pathlib import Path
import re
import struct
import sys
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET


CANONICAL_ORIGIN = "https://stronger-at-home.co.uk"
FORMAL_NAME = "Stronger at Home Physiotherapy"
FORMAL_IDENTITY = "Melanie Watsham trading as Stronger at Home Physiotherapy"
APPROVED_PHONE = "+447843497871"
APPROVED_EMAIL = "melanie@stronger-at-home.co.uk"
APPROVED_EXTERNAL_URLS = {
    "https://ico.org.uk/make-a-complaint/data-protection-complaints/check-if-you-can-complain/",
}

PRIMARY_PAGES = {
    Path("site/index.html"): "/",
    Path("site/about/index.html"): "/about/",
    Path("site/how-i-can-help/index.html"): "/how-i-can-help/",
    Path("site/appointments-and-fees/index.html"): "/appointments-and-fees/",
    Path("site/contact/index.php"): "/contact/",
}
SUPPORTING_PAGES = {
    Path("site/privacy/index.html"): "/privacy/",
    Path("site/accessibility/index.html"): "/accessibility/",
}
ERROR_PAGES = {Path("site/404.html"): "/404.html"}
HTML_PAGES = PRIMARY_PAGES | SUPPORTING_PAGES | ERROR_PAGES
SITEMAP_URLS = {
    f"{CANONICAL_ORIGIN}{route}" for route in (PRIMARY_PAGES | SUPPORTING_PAGES).values()
}

ALLOWED_BLOCKERS = {
    "privacy-approval",
    "credentials",
    "referral-suitability",
}
EXPECTED_LOGO_SHA256 = "d557a0e8fd05efc86fcca2b3f63d807ad33f29527062697705a8e05616c6db39"
# Update this sorted allowlist only after the complete public source change has
# received content, behaviour and release review. Every regular file under
# site/ belongs here, irrespective of its name or extension.
APPROVED_PUBLIC_SOURCE_SHA256 = {
    "site/.htaccess": "14210b8b14861742ae2dd46317e7c9c40007ad70f778e8378a19e2a07060f6fb",
    "site/404.html": "3412421bbccbb1b4a2159ef8abd5de85ffc46117c885e654427cdd2616fa898a",
    "site/about/index.html": "ec7e6bc1a01af507742ddd8a4019753017b1b9ce073c8dbe17e5b8e91891ae78",
    "site/accessibility/index.html": "06490c62f2a18f948527784c45eaa22d0805e6072e4fe70710a283b7912912bb",
    "site/api/enquiry.php": "ed9d7ece29c3aca98e35d6382661daac6df33bed6a6c5339aceb519fbd05d270",
    "site/api/src/EnquiryController.php": "f58b674470922b4b741cc038ee7ce4efe8e021c5b53ca37a1cde7d5b21b56d06",
    "site/api/src/EnquiryMessage.php": "715d322e3bbe1d02c117e9ed698798c27bd2622ee603789d844b6a3b4d5fffc9",
    "site/api/src/EnquiryValidator.php": "e490d6c2257e3d6b23bba898d9887fc7507636f17649511f2699b02409026076",
    "site/api/src/FileRateLimiter.php": "582eef482c4d8f0677760e708589bf38b57e53e260da1d780d822402ac444348",
    "site/api/src/MailTransport.php": "215635fb7295bd51f9865e5559cb2b649f49249771e54902c44eb05415ac825b",
    "site/api/src/PhpMailerTransport.php": "2fb41428112e7b70cf31e8d984ef370ee6d8055456a346c406530c6d5df95dff",
    "site/api/src/RateLimit.php": "2e1f975f955d86222f2474b66ecaaa2074279a30ce445a8401b2a6b4753aff7a",
    "site/api/src/Response.php": "47fe950982fd6a7bb84bcf50e7346b644a46b6b8cee414fc44dd7f44f67214c1",
    "site/api/src/ValidationResult.php": "2ceb38671310bd93cb04ebcbcd1341bcfbc15bf069229a5b375e258772ff1898",
    "site/appointments-and-fees/index.html": "c7f00698a41ed12cd7de31c4b97e0f026b47bca2079a7832e5040717098f2ce8",
    "site/assets/css/brand-tokens.css": "9945f6e139a26124a0755d46e0bb4dc93f3e867d87278b0ff4988d0f92d40450",
    "site/assets/css/site.css": "d81c6766c840d76cbcfd2f26e30d652597471b3fb024089e0541f1ced2235fa2",
    "site/assets/fonts/atkinson-hyperlegible-next.ttf": "5a455d1cfa099b601ab70751bb9673e8fe1854dc4500c80e1a220d0d75e31745",
    "site/assets/fonts/OFL-atkinson.txt": "09636801ed3e868736cc359bb1c819c5ef76529cbb41473cb1f602ef166dad0a",
    "site/assets/fonts/OFL-source-serif.txt": "0fd8b796c1c6220a559a5682cfd00d1c8488b428369f7cb70deb671888cef85f",
    "site/assets/fonts/source-serif-4.ttf": "97b2d4da6e3cb494b5a1e66ae176914d852ccabef49e0c02c0df25f3e39aca0b",
    "site/assets/images/melanie-watsham-portrait.jpg": "9f5b50683414293d1fecb9b6ba0eb644259cd6007c4e309b51777a05651f5718",
    "site/assets/images/stronger-at-home-logo.png": EXPECTED_LOGO_SHA256,
    "site/assets/js/site.js": "3719a73b082b915082cc65fd4369e9e970e48629912377f52b9e44467ad42b07",
    "site/contact/index.php": "c648dae8718c26bfdc857b9e129fc9006f1a3c8b9d763894f3308521dc5d8b46",
    "site/how-i-can-help/index.html": "e2d029ce0e335ef785cd9e0c78992dd061b9ebc81a585d50f0a99ba7db87f416",
    "site/index.html": "3faa795c7fbc7ffc57352a2272d8d08a4d69d2898f047e0f2faf30cf56763fc0",
    "site/privacy/index.html": "ce85373512657f372f321b7527225326adf8907e23ba35f1a98317728f182b6b",
    "site/robots-staging.txt": "331ea9090db0c9f6f597bd9840fd5b171830f6e0b3ba1cb24dfa91f0c95aedc1",
    "site/robots.txt": "6806d9c899e6b514b73f45b56f6ff0eb6193e996027444ecebc88d4c31bbf294",
    "site/sitemap.xml": "e343bdfdc81a434ba772c17174e8f36fe79fdab8e3b52d03b63e3d7976469101",
}
EXPECTED_JSON_LD = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": FORMAL_NAME,
    "url": f"{CANONICAL_ORIGIN}/",
    "telephone": APPROVED_PHONE,
    "email": APPROVED_EMAIL,
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "11 Mospey Crescent",
        "addressLocality": "Epsom",
        "addressRegion": "Surrey",
        "postalCode": "KT17 4LZ",
        "addressCountry": "GB",
    },
    "areaServed": "Approximately 10 miles around Epsom, Surrey",
}
PROHIBITED_CLAIMS = {
    "hcpc",
    "csp",
    "agile",
    "atocp",
    "guarantee",
    "guaranteed",
    "testimonial",
    "testimonials",
    "cure",
    "cures",
    "emergency",
}
PROHIBITED_PHRASES = {
    "referral suitability",
    "referral exclusion",
    "not suitable for",
    "we cannot help",
    "we do not treat",
}
PROHIBITED_PUBLIC_PATTERNS = {
    "eligibility, suitability, exclusion or restriction claim": (
        r"\b(?:eligibility|eligible|suitability|suitable|exclusions?|restrictions?|restricted)\b"
        r"|\b(?:not|only)\s+available\s+(?:to|for)\b"
        r"|\bwe\s+(?:only|do\s+not|cannot)\s+(?:see|support|treat|accept)\b"
        r"|\b(?:patients?|people|adults)\s+must\s+be\b"
        r"|\breferral(?:\s+is)?\s+required\b"
    ),
    "registered or credential mark claim": (
        r"[®™]|\b(?:registered|chartered|licen[cs]ed|accredited|certified|qualified)\s+physiotherapist\b"
    ),
    "transaction method wording": (
        r"\b(?:payments?|cash|cheques?|bacs|paypal|invoices?)\b"
        r"|\b(?:bank\s+transfers?|direct\s+debits?|standing\s+orders?)\b"
        r"|\b(?:bank\s+details|sort\s+code|account\s+number)\b"
        r"|\b(?:credit|debit|payment)\s+cards?\b|\b(?:apple|google)\s+pay\b"
        r"|\bpay(?:ing|able|s|ed)?\s+by\b"
        r"|\bwe\s+accept\s+(?:cash|cheques?|cards?|bacs|paypal|apple\s+pay|google\s+pay)\b"
    ),
    "walk-in, drop-in or clinic wording": r"\b(?:walk|drop)[\s-]*in\b|\bclinics?\b",
}
EXPECTED_HTACCESS = (
    "Options -Indexes\n"
    "ErrorDocument 404 /404.html\n"
    "RewriteEngine On\n"
    "RewriteCond %{HTTP_HOST} !^(?:stronger-at-home\\.co\\.uk|www\\.stronger-at-home\\.co\\.uk|staging\\.stronger-at-home\\.co\\.uk)$ [NC]\n"
    "RewriteRule ^ - [R=400,L]\n"
    "RewriteCond %{HTTP_HOST} ^www\\.stronger-at-home\\.co\\.uk$ [NC]\n"
    "RewriteRule ^ https://stronger-at-home.co.uk%{REQUEST_URI} [R=301,L]\n"
    "RewriteCond %{HTTPS} !=on\n"
    "RewriteCond %{HTTP_HOST} ^(?:stronger-at-home\\.co\\.uk|staging\\.stronger-at-home\\.co\\.uk)$ [NC]\n"
    "RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]\n"
    'Header always set X-Content-Type-Options "nosniff"\n'
    'Header always set Referrer-Policy "strict-origin-when-cross-origin"\n'
    'Header always set Permissions-Policy "camera=(), microphone=(), geolocation=()"\n'
    'Header always set Content-Security-Policy "default-src \'self\'; img-src \'self\'; style-src \'self\'; script-src \'self\'; form-action \'self\'; base-uri \'self\'; frame-ancestors \'none\'"\n'
)


class SiteHTMLParser(HTMLParser):
    """Collect only the document facts needed by the release validator."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[str] = []
        self.ids: set[str] = set()
        self.h1_count = 0
        self.title_parts: list[str] = []
        self._in_title = False
        self._ignored_text_depth = 0
        self.visible_parts: list[str] = []
        self.visitor_attributes: list[str] = []
        self.meta: dict[str, list[str]] = {}
        self.canonicals: list[str] = []
        self.references: list[tuple[str, str, str]] = []
        self.images: list[dict[str, str | None]] = []
        self.blockers: list[str] = []
        self.json_ld_parts: list[list[str]] = []
        self._active_json_ld: list[str] | None = None
        self.controls: list[tuple[str, dict[str, str | None]]] = []
        self.explicit_label_targets: set[str] = set()
        self.nested_label_targets: set[str] = set()
        self._label_depth = 0
        self.form_attributes: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.tags.append(tag)
        self.visitor_attributes.extend(
            str(attributes[name])
            for name in ("alt", "aria-label", "title", "placeholder")
            if attributes.get(name)
        )
        if attributes.get("id"):
            self.ids.add(str(attributes["id"]))
        if tag == "h1":
            self.h1_count += 1
        if tag == "title":
            self._in_title = True
        if tag in {"style", "script"}:
            self._ignored_text_depth += 1
        if tag == "script" and attributes.get("type", "").lower() == "application/ld+json":
            self._active_json_ld = []
            self.json_ld_parts.append(self._active_json_ld)
        if tag == "meta":
            key = attributes.get("name") or attributes.get("property")
            if key:
                self.meta.setdefault(str(key).lower(), []).append(str(attributes.get("content") or ""))
        if tag == "link" and "canonical" in str(attributes.get("rel") or "").lower().split():
            self.canonicals.append(str(attributes.get("href") or ""))
        for attribute in ("href", "src", "action"):
            value = attributes.get(attribute)
            if value:
                self.references.append((tag, attribute, str(value)))
        if tag == "img":
            self.images.append(attributes)
        blocker = attributes.get("data-production-blocker")
        if blocker:
            self.blockers.append(str(blocker))
        if tag == "label":
            self._label_depth += 1
            if attributes.get("for"):
                self.explicit_label_targets.add(str(attributes["for"]))
        if tag in {"input", "select", "textarea"}:
            self.controls.append((tag, attributes))
            if self._label_depth and attributes.get("id"):
                self.nested_label_targets.add(str(attributes["id"]))
        if tag == "form":
            self.form_attributes.append(attributes)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag in {"style", "script"}:
            self._ignored_text_depth = max(0, self._ignored_text_depth - 1)
        if tag == "script" and self._active_json_ld is not None:
            self._active_json_ld = None
        if tag == "label":
            self._label_depth = max(0, self._label_depth - 1)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._active_json_ld is not None:
            self._active_json_ld.append(data)
        if self._ignored_text_depth == 0:
            self.visible_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())

    @property
    def visible_text(self) -> str:
        return " ".join(" ".join(self.visible_parts).split())


def _read_text(path: Path, errors: list[str], label: str) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"Missing required file: {label}")
    except UnicodeDecodeError:
        errors.append(f"Required text file is not UTF-8: {label}")
    return None


def _validate_public_content_approval(root: Path, errors: list[str]) -> None:
    site_root = root / "site"
    public_sources: dict[str, Path] = {}
    public_directories: set[str] = set()

    def scan_directory(directory: Path) -> None:
        relative_directory = directory.relative_to(root).as_posix()
        public_directories.add(relative_directory)
        try:
            entries = sorted(directory.iterdir(), key=lambda item: item.name)
        except OSError as error:
            errors.append(
                f"Public tree approval drift: unreadable directory {relative_directory}: {error}"
            )
            return
        for path in entries:
            relative_path = path.relative_to(root).as_posix()
            if path.is_symlink():
                errors.append(f"Public tree approval drift: symlink {relative_path}")
            elif path.is_dir():
                scan_directory(path)
            elif path.is_file():
                public_sources[relative_path] = path
            else:
                errors.append(f"Public tree approval drift: special entry {relative_path}")

    if site_root.is_symlink():
        errors.append("Public tree approval drift: symlink site")
    elif site_root.is_dir():
        scan_directory(site_root)
    elif site_root.exists():
        errors.append("Public tree approval drift: site is not a directory")

    approved_paths = set(APPROVED_PUBLIC_SOURCE_SHA256)
    actual_paths = set(public_sources)
    approved_directories = {"site"}
    for approved_path in approved_paths:
        parent = Path(approved_path).parent
        while parent.as_posix() not in {".", ""}:
            approved_directories.add(parent.as_posix())
            parent = parent.parent

    for path in sorted(public_directories - approved_directories):
        errors.append(f"Public tree approval drift: added directory {path}")
    for path in sorted(approved_directories - public_directories):
        errors.append(f"Public tree approval drift: removed directory {path}")
    for path in sorted(actual_paths - approved_paths):
        errors.append(f"Public content approval drift: added {path}")
    for path in sorted(approved_paths - actual_paths):
        errors.append(f"Public content approval drift: removed {path}")
    for path in sorted(approved_paths & actual_paths):
        source = public_sources[path]
        if source.is_symlink() or not source.is_file():
            errors.append(f"Public content approval drift: changed {path}")
            continue
        actual_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        if actual_hash != APPROVED_PUBLIC_SOURCE_SHA256[path]:
            errors.append(f"Public content approval drift: changed {path}")


def _parse_pages(root: Path, errors: list[str]) -> dict[Path, SiteHTMLParser]:
    parsed: dict[Path, SiteHTMLParser] = {}
    for relative_path in HTML_PAGES:
        text = _read_text(root / relative_path, errors, relative_path.as_posix())
        if text is None:
            continue
        parser = SiteHTMLParser()
        try:
            parser.feed(text)
            parser.close()
        except Exception as error:  # HTMLParser can surface malformed entities.
            errors.append(f"Could not parse {relative_path.as_posix()}: {error}")
            continue
        parsed[relative_path] = parser
    return parsed


def _validate_structure_and_metadata(
    parsed: dict[Path, SiteHTMLParser], errors: list[str]
) -> None:
    seen_titles: dict[str, Path] = {}
    seen_descriptions: dict[str, Path] = {}
    for relative_path, route in HTML_PAGES.items():
        parser = parsed.get(relative_path)
        if parser is None:
            continue
        label = relative_path.as_posix()
        if parser.h1_count != 1:
            errors.append(f"{label} must contain exactly one h1 (found {parser.h1_count})")
        missing_landmarks = {"header", "nav", "main", "footer"} - set(parser.tags)
        if missing_landmarks:
            errors.append(f"{label} is missing landmarks: {', '.join(sorted(missing_landmarks))}")

        if not parser.title:
            errors.append(f"{label} is missing a title")
        elif parser.title in seen_titles:
            errors.append(f"Duplicate page title: {parser.title}")
        else:
            seen_titles[parser.title] = relative_path
        descriptions = parser.meta.get("description", [])
        if len(descriptions) != 1 or not descriptions[0].strip():
            errors.append(f"{label} must contain exactly one non-empty description")
            description = ""
        else:
            description = descriptions[0].strip()
            if description in seen_descriptions:
                errors.append(f"Duplicate page description: {description}")
            else:
                seen_descriptions[description] = relative_path

        canonical = f"{CANONICAL_ORIGIN}{route}"
        if parser.canonicals != [canonical]:
            errors.append(f"{label} canonical URL must be {canonical}")
        expected_social = {
            "og:title": parser.title,
            "og:description": description,
            "og:url": canonical,
            "og:type": "website",
        }
        for key, expected in expected_social.items():
            if parser.meta.get(key) != [expected]:
                errors.append(f"{label} {key} must equal {expected}")
        if FORMAL_NAME not in parser.title:
            errors.append(f"{label} title must use the formal business name")
        if FORMAL_IDENTITY not in parser.visible_text:
            errors.append(f"{label} footer must contain the formal sole-trader identity")
        if "Stronger@Home" in parser.visible_text or "Stronger@Home" in parser.title:
            errors.append(f"{label} must spell out Stronger at Home in text")


def _route_to_file(site_root: Path, route: str) -> Path | None:
    relative = unquote(route).lstrip("/")
    if not relative:
        candidate = site_root / "index.html"
        return candidate if candidate.is_file() else None
    candidate = site_root / relative
    if candidate.is_file():
        return candidate
    if route.endswith("/"):
        for index_name in ("index.html", "index.php"):
            index = candidate / index_name
            if index.is_file():
                return index
    return None


def _validate_links(root: Path, parsed: dict[Path, SiteHTMLParser], errors: list[str]) -> None:
    site_root = root / "site"
    required_routes = set(PRIMARY_PAGES.values()) | {"/contact/#appointment-request"}
    required_footer_routes = {"/privacy/", "/accessibility/"}
    for relative_path, parser in parsed.items():
        source_route = HTML_PAGES[relative_path]
        hrefs = {value for tag, attribute, value in parser.references if tag == "a" and attribute == "href"}
        if not required_routes.issubset(hrefs):
            missing = sorted(required_routes - hrefs)
            errors.append(f"{relative_path.as_posix()} is missing primary links: {', '.join(missing)}")
        if not required_footer_routes.issubset(hrefs):
            errors.append(f"{relative_path.as_posix()} is missing privacy or accessibility footer links")

        for tag, attribute, value in parser.references:
            parts = urlsplit(value)
            if parts.scheme in {"mailto", "tel"}:
                approved = APPROVED_EMAIL if parts.scheme == "mailto" else APPROVED_PHONE
                if parts.path != approved:
                    errors.append(f"Unapproved {parts.scheme} contact in {relative_path.as_posix()}: {parts.path}")
                continue
            if parts.scheme and parts.scheme not in {"http", "https"}:
                errors.append(f"Unsupported link scheme in {relative_path.as_posix()}: {value}")
                continue
            if parts.scheme in {"http", "https"}:
                if (
                    f"{parts.scheme}://{parts.netloc}" != CANONICAL_ORIGIN
                    and value not in APPROVED_EXTERNAL_URLS
                ):
                    errors.append(f"External URL is not approved in {relative_path.as_posix()}: {value}")
                    continue
                if value in APPROVED_EXTERNAL_URLS:
                    continue
                target_route = parts.path or "/"
            else:
                absolute = urlsplit(urljoin(f"{CANONICAL_ORIGIN}{source_route}", value))
                target_route = posixpath.normpath(absolute.path)
                if absolute.path.endswith("/") and target_route != "/":
                    target_route += "/"
                if not target_route.startswith("/"):
                    target_route = f"/{target_route}"
                parts = absolute
            target = _route_to_file(site_root, target_route)
            if target is None:
                errors.append(
                    f"Missing local target in {relative_path.as_posix()} for {tag} {attribute}: {value}"
                )
                continue
            if parts.fragment:
                target_relative = target.relative_to(root)
                target_parser = parsed.get(target_relative)
                if target_parser is None:
                    target_text = _read_text(target, errors, target_relative.as_posix())
                    if target_text is not None:
                        target_parser = SiteHTMLParser()
                        target_parser.feed(target_text)
                if target_parser is not None and unquote(parts.fragment) not in target_parser.ids:
                    errors.append(f"Missing fragment target for {value} in {relative_path.as_posix()}")


def _actual_image_size(path: Path) -> tuple[int, int] | None:
    if path.suffix.lower() == ".png":
        data = path.read_bytes()
        if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
            return None
        return struct.unpack(">II", data[16:24])
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        data = path.read_bytes()
        if len(data) < 4 or data[:2] != b"\xff\xd8":
            return None
        offset = 2
        start_of_frame_markers = {
            0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
            0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
        }
        while offset + 4 <= len(data):
            if data[offset] != 0xFF:
                return None
            while offset < len(data) and data[offset] == 0xFF:
                offset += 1
            if offset >= len(data):
                return None
            marker = data[offset]
            offset += 1
            if marker in {0xD8, 0xD9}:
                continue
            if marker == 0xDA:
                return None
            if offset + 2 > len(data):
                return None
            segment_length = struct.unpack(">H", data[offset:offset + 2])[0]
            if segment_length < 2 or offset + segment_length > len(data):
                return None
            if marker in start_of_frame_markers:
                if segment_length < 7:
                    return None
                height, width = struct.unpack(">HH", data[offset + 3:offset + 7])
                return width, height
            offset += segment_length
    if path.suffix.lower() == ".svg":
        try:
            root = ET.parse(path).getroot()
        except (ET.ParseError, OSError):
            return None
        view_box = root.attrib.get("viewBox", "").split()
        if len(view_box) == 4:
            try:
                return round(float(view_box[2])), round(float(view_box[3]))
            except ValueError:
                return None
    return None


def _validate_images(root: Path, parsed: dict[Path, SiteHTMLParser], errors: list[str]) -> None:
    for relative_path, parser in parsed.items():
        for image in parser.images:
            source = str(image.get("src") or "")
            if "alt" not in image:
                errors.append(f"Image in {relative_path.as_posix()} is missing alt text: {source}")
            width, height = image.get("width"), image.get("height")
            if not width or not height or not str(width).isdigit() or not str(height).isdigit():
                errors.append(f"Image in {relative_path.as_posix()} needs numeric width and height: {source}")
                continue
            source_path = _route_to_file(root / "site", urlsplit(source).path)
            if source_path is None:
                continue
            actual = _actual_image_size(source_path)
            declared = int(str(width)), int(str(height))
            if actual is None:
                errors.append(f"Image dimensions could not be read: {source}")
            elif actual != declared:
                errors.append(f"Image dimensions for {source} must be {actual[0]} × {actual[1]}")

    logo = root / "site/assets/images/stronger-at-home-logo.png"
    brand_logo = root / "brand/assets/source/logo-primary-raster-v2-512.png"
    if logo.is_file():
        logo_hash = hashlib.sha256(logo.read_bytes()).hexdigest()
        if logo_hash != EXPECTED_LOGO_SHA256:
            errors.append("Site raster logo does not match the approved logo bytes")
        if brand_logo.is_file() and logo.read_bytes() != brand_logo.read_bytes():
            errors.append("Site raster logo is not an exact copy of the approved brand asset")


def _validate_exact_asset_copies(root: Path, errors: list[str]) -> None:
    pairs = {
        Path("site/assets/css/brand-tokens.css"): Path("brand/generated/tokens.css"),
        Path("site/assets/fonts/source-serif-4.ttf"): Path("brand/fonts/source-serif-4.ttf"),
        Path("site/assets/fonts/atkinson-hyperlegible-next.ttf"): Path("brand/fonts/atkinson-hyperlegible-next.ttf"),
        Path("site/assets/fonts/OFL-source-serif.txt"): Path("brand/fonts/OFL-source-serif.txt"),
        Path("site/assets/fonts/OFL-atkinson.txt"): Path("brand/fonts/OFL-atkinson.txt"),
    }
    for site_asset, brand_asset in pairs.items():
        site_path, brand_path = root / site_asset, root / brand_asset
        if not site_path.is_file():
            errors.append(f"Missing required file: {site_asset.as_posix()}")
        elif not brand_path.is_file():
            errors.append(f"Missing required file: {brand_asset.as_posix()}")
        elif site_path.read_bytes() != brand_path.read_bytes():
            errors.append(f"Site asset is not an exact approved copy: {site_asset.as_posix()}")


def _validate_forms(parsed: dict[Path, SiteHTMLParser], errors: list[str]) -> None:
    for relative_path, parser in parsed.items():
        labelled = parser.explicit_label_targets | parser.nested_label_targets
        for tag, attributes in parser.controls:
            if tag == "input" and attributes.get("type", "text").lower() == "hidden":
                continue
            identifier = attributes.get("id")
            name = str(attributes.get("name") or identifier or "<unnamed>")
            if not identifier or identifier not in labelled:
                errors.append(f"Form control {name} in {relative_path.as_posix()} needs a label")
    contact = parsed.get(Path("site/contact/index.php"))
    if contact is not None:
        if len(contact.form_attributes) != 1:
            errors.append("Contact page must contain exactly one enquiry form")
        else:
            form = contact.form_attributes[0]
            if str(form.get("method") or "").lower() != "post" or form.get("action") != "/api/enquiry.php":
                errors.append("Contact form must submit by POST to the same-origin enquiry endpoint")


def find_prohibited_content_categories(text: str) -> list[str]:
    """Return narrowly scoped policy categories present in visitor-facing text."""

    categories: list[str] = []
    lower = text.lower()
    for claim in sorted(PROHIBITED_CLAIMS):
        if re.search(rf"\b{re.escape(claim)}\b", lower):
            categories.append(f"unapproved claim: {claim}")
    for phrase in sorted(PROHIBITED_PHRASES):
        if phrase in lower:
            categories.append(f"unapproved claim: {phrase}")
    for category, pattern in sorted(PROHIBITED_PUBLIC_PATTERNS.items()):
        if re.search(pattern, text, re.IGNORECASE):
            categories.append(category)
    return categories


def _validate_contacts_and_claims(
    parsed: dict[Path, SiteHTMLParser], errors: list[str]
) -> None:
    email_pattern = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
    phone_pattern = re.compile(r"\+44\d{10,11}\b")
    for relative_path, parser in parsed.items():
        searchable = " ".join(
            [parser.visible_text, parser.title, *parser.visitor_attributes]
            + [value for values in parser.meta.values() for value in values]
        )
        for category in find_prohibited_content_categories(searchable):
            errors.append(
                f"Prohibited public content in {relative_path.as_posix()}: {category}"
            )
        for email in email_pattern.findall(searchable):
            if email.lower() != APPROVED_EMAIL:
                errors.append(f"Unapproved email address in {relative_path.as_posix()}: {email}")
        for phone in phone_pattern.findall(searchable):
            if phone != APPROVED_PHONE:
                errors.append(f"Unapproved phone number in {relative_path.as_posix()}: {phone}")
        if "Stronger@Home" in searchable:
            errors.append(f"Prose or metadata uses the raster-only wordmark in {relative_path.as_posix()}")

    privacy = parsed.get(Path("site/privacy/index.html"))
    if privacy is not None:
        for required_section in (
            "privacy-controller",
            "privacy-information",
            "privacy-lawful-basis",
            "privacy-sharing",
            "privacy-retention",
            "privacy-rights",
            "privacy-objection",
            "privacy-complaints",
        ):
            if required_section not in privacy.ids:
                errors.append(
                    f"Privacy notice is missing required section: {required_section}"
                )
        for required in (
            FORMAL_IDENTITY,
            "11 Mospey Crescent Epsom Surrey KT17 4LZ",
            APPROVED_EMAIL,
            "name, email address, phone number, preferred contact method, postcode, a short enquiry",
            "detailed or urgent medical information",
            "secure session identifier",
            "rate limit",
            "Article 6(1)(b)",
            "Article 6(1)(c)",
            "Article 6(1)(f)",
            "Article 9(2)(h)",
            "Article 9(2)(f)",
            "GoDaddy",
            "Titan",
            "UK-US Data Bridge",
            "UK International Data Transfer Agreement",
            "standard data protection clauses under Article 46(2)(c)",
            "preferred contact method, postcode, short enquiry and privacy acknowledgement are required",
            "request more information or a copy of the relevant safeguards",
            "12 months after the last contact",
            "eight years after the last treatment",
            "Information Commissioner’s Office",
            "No solely automated decision-making",
        ):
            if required not in privacy.visible_text:
                errors.append(f"Privacy notice is missing required information: {required}")
    contact = parsed.get(Path("site/contact/index.php"))
    if contact is not None:
        hrefs = {
            value
            for tag, attribute, value in contact.references
            if tag == "a" and attribute == "href"
        }
        if f"tel:{APPROVED_PHONE}" not in hrefs or f"mailto:{APPROVED_EMAIL}" not in hrefs:
            errors.append("Contact page must publish the approved phone and email routes")
    accessibility = parsed.get(Path("site/accessibility/index.html"))
    if accessibility is not None:
        for required in ("Web Content Accessibility Guidelines version 2.2 at level AA", APPROVED_EMAIL):
            if required not in accessibility.visible_text:
                errors.append(f"Accessibility page is missing required information: {required}")


def _validate_structured_data(
    parsed: dict[Path, SiteHTMLParser], errors: list[str]
) -> None:
    found_local_businesses: list[tuple[Path, object]] = []
    for relative_path, parser in parsed.items():
        for parts in parser.json_ld_parts:
            raw = "".join(parts).strip()
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as error:
                errors.append(f"Invalid JSON-LD in {relative_path.as_posix()}: {error.msg}")
                continue
            values = value if isinstance(value, list) else [value]
            for item in values:
                if isinstance(item, dict) and item.get("@type") == "LocalBusiness":
                    found_local_businesses.append((relative_path, item))
    if len(found_local_businesses) != 1:
        errors.append("Homepage must contain exactly one LocalBusiness JSON-LD object")
        return
    relative_path, item = found_local_businesses[0]
    if relative_path != Path("site/index.html"):
        errors.append("LocalBusiness JSON-LD must appear only on the homepage")
    if item != EXPECTED_JSON_LD:
        errors.append("LocalBusiness fields must contain only the approved formal facts")


def _validate_crawl_and_headers(root: Path, errors: list[str]) -> None:
    expected_robots = (
        "User-agent: *\n"
        "Allow: /\n"
        "Sitemap: https://stronger-at-home.co.uk/sitemap.xml\n"
    )
    robots = _read_text(root / "site/robots.txt", errors, "site/robots.txt")
    if robots is not None and robots != expected_robots:
        errors.append("Production robots policy must allow crawling and name the canonical sitemap")
    staging = _read_text(
        root / "site/robots-staging.txt", errors, "site/robots-staging.txt"
    )
    if staging is not None and staging != "User-agent: *\nDisallow: /\n":
        errors.append("Staging robots policy must disallow all crawling")

    sitemap_path = root / "site/sitemap.xml"
    if sitemap_path.is_file():
        try:
            sitemap_root = ET.parse(sitemap_path).getroot()
            locations = [
                "".join(element.itertext()).strip()
                for element in sitemap_root.iter()
                if element.tag.rsplit("}", 1)[-1] == "loc"
            ]
            if len(locations) != len(SITEMAP_URLS) or set(locations) != SITEMAP_URLS:
                errors.append("Sitemap routes must exactly match the seven public content pages")
        except ET.ParseError as error:
            errors.append(f"Invalid sitemap XML: {error}")
    else:
        errors.append("Missing required file: site/sitemap.xml")

    htaccess = _read_text(root / "site/.htaccess", errors, "site/.htaccess")
    if htaccess is not None and htaccess != EXPECTED_HTACCESS:
        errors.append("Server directives must exactly match the approved configuration")


def _validate_blockers(
    parsed: dict[Path, SiteHTMLParser], mode: str, errors: list[str]
) -> None:
    blockers = {blocker for parser in parsed.values() for blocker in parser.blockers}
    for blocker in sorted(blockers - ALLOWED_BLOCKERS):
        errors.append(f"Unapproved publication blocker: {blocker}")
    home = parsed.get(Path("site/index.html"))
    if home is not None and "/assets/images/melanie-watsham-portrait.jpg" not in {
        str(image.get("src") or "") for image in home.images
    }:
        errors.append("Homepage must publish the approved Melanie portrait")
    privacy = parsed.get(Path("site/privacy/index.html"))
    if privacy is not None and "Draft for approval" in privacy.visible_text and "privacy-approval" not in blockers:
        errors.append("Draft privacy notice must carry the privacy-approval publication blocker")
    if mode == "production":
        for blocker in sorted(blockers):
            errors.append(f"Production blocker remains: {blocker}")


def validate_site(root: Path, mode: str) -> list[str]:
    """Return deterministic release errors for a project root and environment."""

    if mode not in {"development", "staging", "production"}:
        raise ValueError("mode must be development, staging or production")
    root = Path(root)
    errors: list[str] = []
    _validate_public_content_approval(root, errors)
    parsed = _parse_pages(root, errors)
    _validate_structure_and_metadata(parsed, errors)
    _validate_links(root, parsed, errors)
    _validate_images(root, parsed, errors)
    _validate_exact_asset_copies(root, errors)
    _validate_forms(parsed, errors)
    _validate_contacts_and_claims(parsed, errors)
    _validate_structured_data(parsed, errors)
    _validate_crawl_and_headers(root, errors)
    _validate_blockers(parsed, mode, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        required=True,
        choices=("development", "staging", "production"),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root (defaults to the parent of scripts/).",
    )
    arguments = parser.parse_args(argv)
    errors = validate_site(arguments.root, arguments.mode)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"Site validation passed ({arguments.mode}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
