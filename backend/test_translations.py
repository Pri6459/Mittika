import json
import re
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import translations


class TranslationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        with translations._translation_cache_lock:
            translations._translation_cache.clear()

    def test_curated_copy_uses_reviewed_hindi_and_marathi_translations(self):
        title = "Three-Cup Resin and Wood Tealight Holder"

        self.assertEqual(
            translations._translate_texts([title], "hi"),
            ["तीन टी-लाइट वाला रेज़िन और लकड़ी का होल्डर"],
        )
        self.assertEqual(
            translations._translate_texts([title], "mr"),
            ["तीन छोट्या मेणबत्त्यांसाठी रेझिन व लाकडाचे आधारपात्र"],
        )

    def test_reviewed_marathi_copy_uses_natural_product_wording(self):
        copy = [
            "Hand-painted Terracotta Wall Candle Holder",
            "A red terracotta wall-mounted candle holder with hand-painted white floral motifs and a cup for one tealight.",
            "Hand-woven Striped Cotton Rug",
        ]
        self.assertEqual(
            translations._translate_texts(copy, "mr"),
            [
                "हाताने रंगवलेले मातीचे भिंतीवरचे मेणबत्तीदान",
                "लाल मातीच्या या भिंतीवर लावायच्या मेणबत्तीदानावर पांढऱ्या फुलांची नक्षी हाताने रंगवली आहे. यात एक छोटी मेणबत्ती ठेवता येते.",
                "हातमागावर विणलेली पट्टेदार सुती चटई",
            ],
        )

    def test_unreviewed_product_copy_uses_google_translation(self):
        copy = ["Handwoven Cuff Bracelet", "Handmade necklace description"]
        for language in ("hi", "mr"):
            expected = [f"{language}:{text}" for text in copy]
            with patch.dict("os.environ", {"GOOGLE_CLOUD_TRANSLATE_API_KEY": "test-key"}):
                with patch("translations._google_translate", return_value=expected) as translate:
                    self.assertEqual(translations._translate_texts(copy, language), expected)
            translate.assert_called_once_with(copy, language, "test-key")

    def test_mixes_reviewed_and_google_translations_in_original_order(self):
        reviewed_title = "Three-Cup Resin and Wood Tealight Holder"
        unreviewed_title = "Handwoven Cuff Bracelet"
        with patch.dict("os.environ", {"GOOGLE_CLOUD_TRANSLATE_API_KEY": "test-key"}):
            with patch("translations._google_translate", return_value=["हाथ से बुना कफ ब्रेसलेट"]):
                translated = translations._translate_texts(
                    [reviewed_title, unreviewed_title, reviewed_title],
                    "hi",
                )

        self.assertEqual(
            translated,
            [
                "तीन टी-लाइट वाला रेज़िन और लकड़ी का होल्डर",
                "हाथ से बुना कफ ब्रेसलेट",
                "तीन टी-लाइट वाला रेज़िन और लकड़ी का होल्डर",
            ],
        )

    def test_unreviewed_copy_requires_google_translation_configuration(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(translations.HTTPException) as error:
                translations._translate_texts(["New artisan product"], "hi")

        self.assertEqual(error.exception.status_code, 503)

    def test_google_translation_decodes_entities_and_preserves_request_language(self):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({
            "data": {
                "translations": [
                    {"translatedText": "हार &amp; कंगन"},
                    {"translatedText": "हस्तनिर्मित आभूषण"},
                ]
            }
        }).encode("utf-8")
        texts = ["Necklace & bracelet", "Handmade jewellery"]

        with patch("translations.urlopen", return_value=response) as open_url:
            result = translations._google_translate(texts, "hi", "test-key")

        self.assertEqual(result, ["हार & कंगन", "हस्तनिर्मित आभूषण"])
        request = open_url.call_args.args[0]
        self.assertIn("key=test-key", request.full_url)
        self.assertEqual(
            json.loads(request.data),
            {"q": texts, "target": "hi", "format": "text"},
        )

    def test_reviewed_translations_cover_the_existing_candle_copy(self):
        copy = list(translations._CURATED_PRODUCT_TRANSLATIONS)

        for language in ("hi", "mr"):
            localized = translations._translate_texts(copy, language)
            self.assertEqual(len(localized), len(copy))
            self.assertTrue(all(localized))

    def test_homepage_products_have_reviewed_hindi_and_marathi_copy(self):
        copy = [
            "Carved Wooden Elephant Accent Table",
            "A hand-carved wooden elephant-form stand with a wide bowl-shaped top, suitable as a decorative accent table.",
            "Hand-woven Striped Cotton Rug",
            "A flat-woven cotton floor rug with green geometric stripes and fringed edges.",
            "Embroidered Tree-of-Life Wall Hanging",
            "A teal textile wall hanging embroidered with a flowering tree motif in white, blue, and yellow thread.",
        ]

        for language in ("hi", "mr"):
            localized = translations._translate_texts(copy, language)
            self.assertEqual(len(localized), len(copy))
            self.assertTrue(all(localized))
            self.assertNotEqual(localized, copy)

    def test_visible_jewellery_and_rukhwat_titles_use_reviewed_translations(self):
        titles = [
            "Meenakari Necklace Set",
            "Antique Silver Hoop Earrings",
            "Oxidised Silver Tassel Necklace",
            "Hand-decorated Gift Platter",
            "Hand-painted Miniature Kitchen Set",
            "Decorative Pistachio Shell Birdhouses (Set of 4)",
        ]

        for language in ("hi", "mr"):
            translated = translations._translate_texts(titles, language)
            self.assertEqual(len(translated), len(titles))
            self.assertFalse(any(text == title for text, title in zip(translated, titles)))

    def test_collection_descriptions_have_reviewed_hindi_and_marathi_translations(self):
        descriptions = [
            "A statement necklace set with colorful Meenakari-inspired detailing, made to bring a festive touch to special occasions.",
            "A festive platter dressed with colorful hand-finished details, ready to display or present as a thoughtful gift.",
            "Earthy terracotta chimes bring gentle movement and a warm, handmade accent to a balcony, window, or garden.",
            "A set of miniature divine figurines for a home shrine, prayer space, or thoughtful spiritual gift.",
        ]

        for language in ("hi", "mr"):
            translated = translations._translate_texts(descriptions, language)
            self.assertEqual(len(translated), len(descriptions))
            self.assertTrue(all(text != source for text, source in zip(translated, descriptions)))

    def test_all_collection_product_names_and_descriptions_are_reviewed(self):
        repository_root = Path(__file__).resolve().parents[1]
        category_files = (
            "Jewellery.js",
            "Rukhwat.js",
            "Pottery.js",
            "SpiritualCorner.js",
        )
        source_texts = []
        for filename in category_files:
            source = (
                repository_root / "frontend" / "src" / "components" / filename
            ).read_text(encoding="utf-8")
            source_texts.extend(
                json.loads(value)
                for value in re.findall(
                    r'(?:title|description):\s*("(?:[^"\\]|\\.)*")',
                    source,
                )
            )

        self.assertEqual(len(source_texts), 208)
        for language in ("hi", "mr"):
            translated = translations._translate_texts(source_texts, language)
            self.assertEqual(len(translated), len(source_texts))
            self.assertTrue(
                all(text and text != source for text, source in zip(translated, source_texts))
            )

    def test_candle_and_home_product_names_and_descriptions_are_reviewed(self):
        repository_root = Path(__file__).resolve().parents[1]
        source_texts = []
        for filename in ("Candle.js", "Home.js"):
            source = (
                repository_root / "frontend" / "src" / "components" / filename
            ).read_text(encoding="utf-8")
            source_texts.extend(
                json.loads(value)
                for value in re.findall(
                    r'(?:title|description):\s*("(?:[^"\\]|\\.)*")',
                    source,
                )
            )

        self.assertEqual(len(source_texts), 200)
        for language in ("hi", "mr"):
            translated = translations._translate_texts(source_texts, language)
            self.assertEqual(len(translated), len(source_texts))
            self.assertTrue(
                all(text and text != source for text, source in zip(translated, source_texts))
            )

    def test_unreviewed_product_descriptions_are_machine_translated(self):
        description = (
            "An elegant handmade piece with vibrant colors and detailed craftsmanship."
        )

        for language in ("hi", "mr"):
            expected = f"{language}:अनुवादित वर्णन"
            with patch.dict("os.environ", {"GOOGLE_CLOUD_TRANSLATE_API_KEY": "test-key"}):
                with patch("translations._google_translate", return_value=[expected]):
                    self.assertEqual(
                        translations._translate_texts([description], language),
                        [expected],
                    )

    async def test_route_translates_unreviewed_copy(self):
        request = SimpleNamespace(client=SimpleNamespace(host="test-client"))
        title = "Handmade Silver Necklace"
        body = translations.TranslationRequest(language="mr", texts=[title])
        with patch.dict("os.environ", {"GOOGLE_CLOUD_TRANSLATE_API_KEY": "test-key"}):
            with patch("translations._google_translate", return_value=["हाताने बनवलेला चांदीचा हार"]):
                response = await translations.translate_texts(body, request)

        self.assertEqual(response.translations, ["हाताने बनवलेला चांदीचा हार"])

    async def test_route_returns_reviewed_translation_without_machine_inference(self):
        request = SimpleNamespace(client=SimpleNamespace(host="test-client"))
        title = "Three-Cup Resin and Wood Tealight Holder"
        body = translations.TranslationRequest(language="mr", texts=[title])
        with patch(
            "translations._translate_texts",
            wraps=translations._translate_texts,
        ) as translate:
            response = await translations.translate_texts(body, request)

        self.assertEqual(
            response.translations,
            ["तीन छोट्या मेणबत्त्यांसाठी रेझिन व लाकडाचे आधारपात्र"],
        )
        translate.assert_called_once_with([title], "mr")

    async def test_route_deduplicates_requests_and_preserves_input_order(self):
        request = SimpleNamespace(client=SimpleNamespace(host="test-client"))
        body = translations.TranslationRequest(
            language="hi",
            texts=["First item", "Second item", "First item"],
        )
        with patch.dict("os.environ", {"GOOGLE_CLOUD_TRANSLATE_API_KEY": "test-key"}):
            with patch(
                "translations._google_translate",
                return_value=["पहला", "दूसरा"],
            ) as translate:
                response = await translations.translate_texts(body, request)

        self.assertEqual(
            response.translations,
            ["पहला", "दूसरा", "पहला"],
        )
        translate.assert_called_once_with(["First item", "Second item"], "hi", "test-key")


if __name__ == "__main__":
    unittest.main()
