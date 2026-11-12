import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


class PublicationLinks(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.links = set()
        self.ids = set()
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag in {"a", "link"} and "href" in attrs:
            self.links.add(attrs["href"])


class HubSpotStripePublicationTests(unittest.TestCase):
    def test_recruiter_case_study_and_pdf_are_linked(self):
        docs = Path(__file__).resolve().parents[1] / "docs"
        recruiter = PublicationLinks(docs / "recruiter.html")
        case = PublicationLinks(docs / "hubspot-stripe.html")
        self.assertIn("hubspot-stripe.html", recruiter.links)
        self.assertIn("recruiter.html", case.links)
        self.assertIn("hubspot-stripe-case-study.pdf", recruiter.links & case.links)
        self.assertTrue((docs / "hubspot-stripe-case-study.pdf").read_bytes().startswith(b"%PDF-"))
        for href in case.links:
            link = urlsplit(href)
            if not link.scheme and link.path:
                self.assertTrue((docs / link.path).is_file(), href)
            if not link.scheme and not link.path and link.fragment:
                self.assertIn(link.fragment, case.ids)
