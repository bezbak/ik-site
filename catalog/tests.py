from django.test import TestCase
from django.urls import reverse

from .models import SiteSettings


class SiteLinksTests(TestCase):
    def test_empty_by_default(self):
        data = self.client.get(reverse("catalog:site_links")).json()
        self.assertEqual(data, {"instagram": "", "facebook": "", "x": "", "youtube": ""})

    def test_returns_links_from_admin_settings(self):
        s = SiteSettings.load()
        s.instagram_url = "https://www.instagram.com/avat365/"
        s.youtube_url = "https://www.youtube.com/@avat365"
        s.save()
        data = self.client.get(reverse("catalog:site_links")).json()
        self.assertEqual(data["instagram"], "https://www.instagram.com/avat365/")
        self.assertEqual(data["youtube"], "https://www.youtube.com/@avat365")
        self.assertEqual(data["facebook"], "")
        self.assertEqual(data["x"], "")


class FooterTests(TestCase):
    def test_about_us_has_no_designer_link(self):
        html = self.client.get(reverse("catalog:about_us")).content.decode()
        self.assertNotIn("framergeeks", html)
        self.assertIn("/js/avat-footer.js", html)
