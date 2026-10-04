import unittest
from types import SimpleNamespace
from unittest.mock import patch

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

    def test_unreviewed_product_copy_stays_english_instead_of_getting_bad_translation(self):
        copy = ["Handwoven Cuff Bracelet", "Handmade necklace description"]
        for language in ("hi", "mr"):
            self.assertEqual(translations._translate_texts(copy, language), copy)

    def test_mixes_reviewed_translations_and_english_fallback_in_original_order(self):
        reviewed_title = "Three-Cup Resin and Wood Tealight Holder"
        unreviewed_title = "Handwoven Cuff Bracelet"
        translated = translations._translate_texts(
            [reviewed_title, unreviewed_title, reviewed_title],
            "hi",
        )

        self.assertEqual(
            translated,
            [
                "तीन टी-लाइट वाला रेज़िन और लकड़ी का होल्डर",
                unreviewed_title,
                "तीन टी-लाइट वाला रेज़िन और लकड़ी का होल्डर",
            ],
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

    def test_unreviewed_product_descriptions_use_english_fallback(self):
        description = (
            "An elegant handmade piece with vibrant colors and detailed craftsmanship."
        )

        for language in ("hi", "mr"):
            self.assertEqual(
                translations._translate_texts([description], language),
                [description],
            )

    async def test_route_uses_english_for_unreviewed_copy(self):
        request = SimpleNamespace(client=SimpleNamespace(host="test-client"))
        title = "Handmade Silver Necklace"
        body = translations.TranslationRequest(language="mr", texts=[title])
        response = await translations.translate_texts(body, request)

        self.assertEqual(response.translations, [title])

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
        with patch(
            "translations._enforce_rate_limit",
            wraps=translations._enforce_rate_limit,
        ):
            response = await translations.translate_texts(body, request)

        self.assertEqual(
            response.translations,
            ["First item", "Second item", "First item"],
        )


if __name__ == "__main__":
    unittest.main()
