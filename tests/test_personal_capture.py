import json
import tempfile
import unittest
from pathlib import Path

from tracker.personal_capture import extract_leads, save_leads


class PersonalCaptureTests(unittest.TestCase):
    def test_extracts_dated_10times_event_without_navigation(self):
        html = '''<article><div>04-09 Dec, 2026 · Greater Noida, India</div>
        <a href="/india-itme">India International Textile Machinery Exhibition</a>
        <a href="/newdelhi-in/tradeshows">More events</a></article>'''
        leads = extract_leads(html, "https://10times.com/newdelhi-in/tradeshows", "10times")
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]["title"], "India International Textile Machinery Exhibition")
        self.assertEqual(leads[0]["url"], "https://10times.com/india-itme")
        self.assertIn("Greater Noida", leads[0]["observed_text"])

    def test_extracts_dated_whr_event_and_skips_sign_in(self):
        html = '''<div class="event-card"><a href="/events/urban-transport">
        Urban Transportation Conclave</a><time>02 Mar 2027</time><span>New Delhi</span></div>
        <a href="/signin">Sign in</a>'''
        leads = extract_leads(html, "https://gtm.whr.ai/search", "whr")
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]["url"], "https://gtm.whr.ai/events/urban-transport")

    def test_save_leads_deduplicates_urls(self):
        lead = {"source_site": "10times", "title": "India ITME", "url": "https://10times.com/india-itme",
                "observed_text": "04-09 Dec, 2026", "page_url": "https://10times.com/india/tradeshows"}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "leads.json"
            save_leads(path, [lead])
            save_leads(path, [lead])
            self.assertEqual(len(json.loads(path.read_text(encoding="utf-8"))), 1)


if __name__ == "__main__":
    unittest.main()
