import unittest

from app.taxonomy import classify_job


class TaxonomyTests(unittest.TestCase):
    def test_algorithm_family(self):
        family, confidence, evidence = classify_job("Algorithm Engineer", "AI", "Python and machine learning")
        self.assertEqual(family, "algorithm_ai")
        self.assertGreater(confidence, 0.6)
        self.assertTrue(evidence)

    def test_sales_is_not_promoted_to_technical_family(self):
        family, _, _ = classify_job("Sales Engineer", "Sales", "Customer development")
        self.assertEqual(family, "sales")

    def test_title_beats_incidental_ai_in_description(self):
        family, _, _ = classify_job("人力资源（统招）", "职能", "AI tools and machine learning are a plus")
        self.assertEqual(family, "functional")

    def test_controlled_category_beats_incidental_description_keyword(self):
        family, _, _ = classify_job("投放运营实习生", "市场/销售", "Use AI to improve campaign operations")
        self.assertEqual(family, "operations")


if __name__ == "__main__":
    unittest.main()
