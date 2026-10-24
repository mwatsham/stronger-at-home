"""Deterministic, fail-closed transformation of an approved public snapshot."""
from pathlib import Path
import re


DISABLED_ENDPOINT = '''<?php
declare(strict_types=1);
http_response_code(503);
header('Content-Type: text/plain; charset=UTF-8');
header('Cache-Control: no-store');
echo "Online appointment requests are temporarily unavailable.\\n";
exit;
'''


def replace_one(content: str, pattern: str, replacement: str) -> str:
    content, count = re.subn(pattern, lambda _: replacement, content, flags=re.DOTALL)
    if count != 1:
        raise ValueError(f"Informational source structure changed: expected one match, got {count}")
    return content


def paragraph(content: str, start: str, replacement: str) -> str:
    return replace_one(content, r"<p>" + re.escape(start) + r"[^<]*(?:<(?!/p>)[^<]*)*</p>",
                       f"<p>{replacement}</p>" if replacement else "")


def prepare_informational_public_tree(public_root: Path) -> None:
    """Remove active enquiry behavior, adjusting public copy in the build only."""
    contact_path = public_root / "contact/index.php"
    contact = contact_path.read_text(encoding="utf-8")
    contact = replace_one(contact, r"\A<\?php.*?\?>\s*(?=<!doctype html>)", "")
    contact = replace_one(contact, r'<form class="appointment-form".*?</form>',
                          '<div class="section-heading narrow-heading">\n        <p class="notice">Online appointment requests are temporarily unavailable.</p>\n      </div>')
    contact = replace_one(contact, re.escape("You can request an appointment by email, phone or this website enquiry form."),
                          "You can contact Melanie by email or phone.")
    contact = contact.replace("Website enquiry", "Online appointments")
    if "<?" in contact or "<form" in contact:
        raise ValueError("Informational contact must be static and contain no form")
    contact_path.write_text(contact, encoding="utf-8")
    (public_root / "api/enquiry.php").write_text(DISABLED_ENDPOINT, encoding="utf-8")

    privacy_path = public_root / "privacy/index.html"
    privacy = privacy_path.read_text(encoding="utf-8")
    privacy = privacy.replace("information submitted through this website", "information associated with this website and direct enquiries")
    privacy = privacy.replace("information submitted through the website", "website information and direct enquiries")
    privacy = privacy.replace("Last updated: 7 September 2026.", "Last updated: 24 October 2026.")
    privacy = paragraph(privacy, "You provide the information directly.",
        "The website appointment-request form is temporarily disabled while the ICO application is in progress. This website does not accept appointment-form submissions. You can contact Melanie directly by email or phone; those channels remain subject to data protection obligations.")
    privacy = paragraph(privacy, "This information is used to receive", 
        "If you contact Melanie directly, the contact details and enquiry you provide are used to respond and discuss availability. Please do not send detailed or urgent medical information.")
    privacy = paragraph(privacy, "Your name, preferred contact method, postcode,", 
        "Contacting Melanie does not confirm an appointment. There is no statutory requirement to provide enquiry information.")
    privacy = privacy.replace("keeping the website and enquiry form secure", "keeping the website secure")
    privacy = paragraph(privacy, "The privacy checkbox confirms", "")
    privacy = paragraph(privacy, "A secure session identifier supports", 
        "The disabled website form does not start a session, set a form-security cookie or process submissions. The website’s own code does not set advertising or analytics cookies. The third-party review widget is described below.")
    privacy = paragraph(privacy, "To reduce repeated automated submissions,", 
        "The disabled enquiry endpoint does not store form rate-limit identifiers or send appointment emails. Hosting logs may still record requests to that address.")
    privacy = paragraph(privacy, "Appointment enquiries are delivered to Melanie.",
        "Direct enquiries by email are received by Melanie through Titan, the email provider. GoDaddy processes website and server information as the hosting provider. Their authorised service providers may also process information where necessary to supply, secure and support those services.")
    privacy_path.write_text(privacy, encoding="utf-8")

    for path in sorted(public_root.rglob("*")):
        if path.suffix in {".html", ".shtml", ".php"} and "api" not in path.relative_to(public_root).parts:
            content = path.read_text(encoding="utf-8")
            content = content.replace("Request an appointment", "Contact Melanie")
            path.write_text(content, encoding="utf-8")
