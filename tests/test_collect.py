import unittest

from tracker.collect import discover_event_links, scan_sources


def approved(url):
    return {"id": url, "url": url, "enabled": True, "permitted_use": "ALLOW", "max_depth": 0}


class CollectionTests(unittest.TestCase):
    def test_follows_relevant_event_links_on_new_source(self):
        html = '''<a href="/events/india-fashion-expo-2027">India Fashion Expo 2027</a>
        <a href="/about">About us</a>
        <a href="https://other.example/2027/book-fair">Book Fair 2027</a>'''
        included, rejected = discover_event_links("https://organizer.example/calendar", html)
        links = {item["url"] for item in included}
        self.assertIn("https://organizer.example/events/india-fashion-expo-2027", links)
        self.assertIn("https://other.example/2027/book-fair", {item["url"] for item in rejected})
        self.assertNotIn("https://organizer.example/about", links)

    def test_scan_source_reports_candidates_from_fetched_page(self):
        result = scan_sources(
            [approved("https://organizer.example/calendar")],
            fetch_html=lambda url: '<a href="/events/home-expo-2027">Home Expo 2027</a>',
        )
        self.assertEqual(result["sources"][0]["outcome"], "SUCCESS_WITH_EVENTS")
        self.assertEqual(result["candidate_links"], ["https://organizer.example/events/home-expo-2027"])

    def test_discovers_generic_link_from_dated_event_card(self):
        html = '''<ul class="slider"><li class="item"><div class="content">
        Delhi 29 - 31 July, 2027 <a href="/del/">Explore Now</a>
        </div></li></ul>'''
        included, _ = discover_event_links("https://giftsworldexpo.com/", html)
        self.assertEqual(len(included), 1)
        self.assertEqual(included[0]["url"], "https://giftsworldexpo.com/del")
        self.assertIn("Delhi", included[0]["observed_date_city_text"])
        self.assertIn("2027", included[0]["observed_date_city_text"])
        self.assertIn("2027", included[0]["label"])

    def test_scan_sources_deduplicates_links_across_pages(self):
        html = '<a href="https://event.example/home-expo-2027">Home Expo 2027</a>'
        result = scan_sources(
            [approved("https://event.example/one"), approved("https://event.example/two")],
            fetch_html=lambda url: html,
        )
        self.assertEqual(len(result["sources"]), 2)
        self.assertEqual(result["candidate_links"], ["https://event.example/home-expo-2027"])


if __name__ == "__main__":
    unittest.main()
