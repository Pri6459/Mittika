import unittest

from ml_engine import MittikaMLEngine


class CategoryPredictionTests(unittest.TestCase):
    def setUp(self):
        self.engine = MittikaMLEngine()

    def test_recognizes_examples_from_each_product_category(self):
        examples = {
            "Ear cuffling": "Handmade Jewellery",
            "Small terracotta planter": "Pottery Art",
            "Vanilla scented candle": "Candle and Resin Art",
            "Rukhwat wedding thali": "Rukhwat Art",
            "Ganesha pooja idol": "Spiritual Art",
            "Wooden wall mirror": "Home Decor",
        }

        for title, expected_category in examples.items():
            with self.subTest(title=title):
                prediction = self.engine.predict_category(title)
                self.assertEqual(prediction["predictedCategory"], expected_category)
                self.assertGreaterEqual(prediction["confidence"], 0.55)

    def test_returns_uncertain_without_category_evidence(self):
        prediction = self.engine.predict_category("Handcrafted item")

        self.assertEqual(prediction["predictedCategory"], "Uncertain")
        self.assertEqual(prediction["confidence"], 0.0)
        self.assertTrue(all(value == 0.0 for value in prediction["probabilities"].values()))

    def test_returns_uncertain_when_category_evidence_is_ambiguous(self):
        prediction = self.engine.predict_category("Macrame")

        self.assertEqual(prediction["predictedCategory"], "Uncertain")
        self.assertLess(prediction["confidence"], 0.55)


if __name__ == "__main__":
    unittest.main()
