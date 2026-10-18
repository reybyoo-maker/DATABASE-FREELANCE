import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import runner


def prospect(name, country, industry, evidence="", **kwargs):
    row = {
        "company_name": name,
        "country": country,
        "city": "Jakarta",
        "industry": industry,
        "evidence": evidence,
        "source_name": "Test fixture",
        "data_quality": "Test data",
        "instagram": "",
        "facebook": "",
        "linkedin": "",
        "tiktok": "",
        "other_social": "",
        "whatsapp_url": "",
        "public_email": "",
        "public_phone": "",
        "website": "",
    }
    row.update(kwargs)
    return row


class PortfolioMatchTests(unittest.TestCase):
    def test_skincare_shop_matches_customer_chat_example(self):
        row = prospect("Toko Skincare Contoh", "Indonesia", "e-commerce brand", "skincare products")
        offer = runner.choose_portfolio_offer(row)
        self.assertEqual(offer["url"], "https://agencyai.reybyoo.workers.dev/portfolio/toko-skincare-chat-ai")

    def test_fashion_brand_matches_content_example(self):
        row = prospect("Contoh Fashion Brand", "Indonesia", "fashion store")
        offer = runner.choose_portfolio_offer(row)
        self.assertEqual(offer["url"], "https://agencyai.reybyoo.workers.dev/portfolio/brand-fashion-content")

    def test_restaurant_with_instagram_matches_dm_example(self):
        row = prospect("Contoh Cafe", "Indonesia", "restaurant", instagram="https://instagram.com/example_cafe")
        offer = runner.choose_portfolio_offer(row)
        self.assertEqual(offer["url"], "https://agencyai.reybyoo.workers.dev/portfolio/dm-instagram-otomatis")

    def test_software_company_matches_b2b_lead_example(self):
        row = prospect("Example Software", "United States", "software company")
        offer = runner.choose_portfolio_offer(row)
        self.assertEqual(offer["url"], "https://agencyai.reybyoo.workers.dev/portfolio/jasa-b2b-lead-engine")

    def test_fallback_messages_include_agency_and_relevant_example(self):
        row = prospect(
            "Contoh Cafe", "Indonesia", "restaurant",
            evidence="Public Instagram business profile",
            instagram="https://instagram.com/example_cafe",
        )
        runner.template_fallback(row, "Simulated model outage")
        expected_example = "https://agencyai.reybyoo.workers.dev/portfolio/dm-instagram-otomatis"
        for field in ("outreach_dm", "outreach_whatsapp", "outreach_email_body"):
            with self.subTest(field=field):
                self.assertIn("[nama kamu]", row[field].lower())
                self.assertIn("aga-ai growth agency", row[field].lower())
                self.assertIn(runner.AGENCY_PORTFOLIO_URL, row[field])
                self.assertIn(expected_example, row[field])
        self.assertEqual(row["relevant_portfolio_url"], expected_example)
        self.assertEqual(row["portfolio_service_match"], "Balas komentar & DM Instagram")


if __name__ == "__main__":
    unittest.main()
