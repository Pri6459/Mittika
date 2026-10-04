import collections
import threading
import time
from collections import OrderedDict
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/translations", tags=["Translations"])
MAX_BATCH_CHARACTERS = 20000
MAX_TEXT_LENGTH = 20000
MAX_REQUESTS_PER_MINUTE = 30
MAX_CHARACTERS_PER_MINUTE = 100000
_rate_limit_lock = threading.Lock()
_translation_usage = {}
_translation_cache_lock = threading.Lock()
_translation_cache = OrderedDict()
MAX_CACHED_TRANSLATIONS = 10000
_CURATED_PRODUCT_TRANSLATIONS = {
    "Meenakari Necklace Set": {
        "hi": "मीनाकारी हार का सेट",
        "mr": "मीनाकारी नक्षीकामाचा हार-संच",
    },
    "Antique Silver Hoop Earrings": {
        "hi": "पुराने अंदाज़ के चाँदी के गोल झुमके",
        "mr": "पुरातन शैलीतील चांदीची गोल कर्णभूषणे",
    },
    "Oxidised Silver Tassel Necklace": {
        "hi": "ऑक्सिडाइज़्ड चाँदी और लटकनों वाला हार",
        "mr": "ऑक्सिडाइझ्ड चांदीचा झुबक्यांचा हार",
    },
    "Hand-decorated Gift Platter": {
        "hi": "हाथ से सजी उपहार की थाली",
        "mr": "हाताने सजवलेली भेटवस्तूची थाळी",
    },
    "Hand-painted Miniature Kitchen Set": {
        "hi": "हाथ से चित्रित छोटा रसोई सेट",
        "mr": "हाताने रंगवलेला छोटेखानी स्वयंपाकघराचा संच",
    },
    "Decorative Pistachio Shell Birdhouses (Set of 4)": {
        "hi": "पिस्ते के छिलकों से बने सजावटी पक्षीघर (4 का सेट)",
        "mr": "पिस्त्याच्या टरफलांपासून बनवलेली सजावटी पक्ष्यांची घरटी (४ चा संच)",
    },
    "Carved Wooden Elephant Accent Table": {
        "hi": "नक्काशीदार लकड़ी की हाथी के आकार वाली सजावटी मेज़",
        "mr": "हत्तीच्या आकाराचे कोरीव लाकडी सजावटी टेबल",
    },
    "A hand-carved wooden elephant-form stand with a wide bowl-shaped top, suitable as a decorative accent table.": {
        "hi": "हाथी के आकार का हाथ से तराशा हुआ लकड़ी का स्टैंड, जिसके ऊपर चौड़ा कटोरे जैसा हिस्सा है। इसे सजावटी मेज़ की तरह रखा जा सकता है।",
        "mr": "हत्तीच्या आकाराचा हाताने कोरलेला लाकडी स्टँड. त्याचा वरचा भाग रुंद व वाटीसारखा असून, सजावटीच्या टेबलाप्रमाणे वापरता येतो.",
    },
    "Hand-woven Striped Cotton Rug": {
        "hi": "हाथ से बुना धारीदार सूती गलीचा",
        "mr": "हातमागावर विणलेली पट्टेदार सुती चटई",
    },
    "A flat-woven cotton floor rug with green geometric stripes and fringed edges.": {
        "hi": "हरे ज्यामितीय पैटर्न वाली और झालरदार किनारों की हाथ से बुनी सूती फर्श की चटाई।",
        "mr": "हिरव्या भौमितिक पट्ट्यांचा आणि झालरदार कडा असलेला हातमागावर विणलेला सुती गालिचा.",
    },
    "Embroidered Tree-of-Life Wall Hanging": {
        "hi": "जीवन-वृक्ष की कढ़ाई वाली दीवार सजावट",
        "mr": "जीवनवृक्षाच्या भरतकामाची भिंतीवरील सजावट",
    },
    "A teal textile wall hanging embroidered with a flowering tree motif in white, blue, and yellow thread.": {
        "hi": "नील-हरे कपड़े पर सफेद, नीले और पीले धागों से फूलों वाले वृक्ष की कढ़ाई की गई दीवार सजावट।",
        "mr": "हिरवट निळ्या कापडावर पांढऱ्या, निळ्या व पिवळ्या धाग्यांनी फुललेल्या वृक्षाचे भरतकाम केले आहे. ही कापडी सजावट भिंतीवर टांगता येते.",
    },
    "Resin-Art Nesting Tables (Set of 3)": {
        "hi": "रेज़िन आर्ट वाले नेस्टिंग टेबल (3 का सेट)",
        "mr": "एकात एक मावणाऱ्या रेझिन कलाकामाच्या तीन लाकडी मेजांचा संच",
    },
    "Three wooden nesting tables with glossy black tabletops decorated with swirling white and gold resin-art patterns.": {
        "hi": "चमकदार काले टॉप पर सफेद और सुनहरे रंग के घुमावदार रेज़िन-आर्ट डिज़ाइन वाले लकड़ी के तीन नेस्टिंग टेबल।",
        "mr": "एकात एक मावणाऱ्या तीन लाकडी मेजांच्या चमकदार काळ्या पृष्ठभागांवर पांढऱ्या व सोनेरी रंगांची वळणदार रेझिन नक्षी आहे.",
    },
    "Hand-painted Terracotta Wall Candle Holder": {
        "hi": "हाथ से चित्रित टेराकोटा वॉल कैंडल होल्डर",
        "mr": "हाताने रंगवलेले मातीचे भिंतीवरचे मेणबत्तीदान",
    },
    "A red terracotta wall-mounted candle holder with hand-painted white floral motifs and a cup for one tealight.": {
        "hi": "सफेद फूलों की हाथ से चित्रित नक्काशी वाला लाल टेराकोटा वॉल कैंडल होल्डर। इसमें एक टी-लाइट रखने की जगह है।",
        "mr": "लाल मातीच्या या भिंतीवर लावायच्या मेणबत्तीदानावर पांढऱ्या फुलांची नक्षी हाताने रंगवली आहे. यात एक छोटी मेणबत्ती ठेवता येते.",
    },
    "Textured Bowl Candles": {
        "hi": "कटोरीनुमा पात्रों में मोमबत्तियाँ",
        "mr": "नक्षीदार वाट्यांमधील मेणबत्त्या",
    },
    "Candles set in white textured, bowl-shaped holders with hand-finished carved and painted patterns.": {
        "hi": "सफेद, बनावटदार कटोरीनुमा पात्रों में रखी मोमबत्तियाँ। हर पात्र पर हाथ से उकेरे और रंगे हुए पैटर्न हैं।",
        "mr": "पांढऱ्या, पोतदार वाट्यांमध्ये ठेवलेल्या मेणबत्त्या. प्रत्येक वाटीवरील नक्षी हाताने कोरून रंगवली आहे.",
    },
    "Three-Cup Resin and Wood Tealight Holder": {
        "hi": "तीन टी-लाइट वाला रेज़िन और लकड़ी का होल्डर",
        "mr": "तीन छोट्या मेणबत्त्यांसाठी रेझिन व लाकडाचे आधारपात्र",
    },
    "A long rectangular holder combining teal-colored resin and natural wood, with spaces for three tealights.": {
        "hi": "नील-हरे रंग के रेज़िन और प्राकृतिक लकड़ी से बना लंबा आयताकार होल्डर, जिसमें तीन टी-लाइट रखने की जगह है।",
        "mr": "हिरवट निळे रेझिन आणि नैसर्गिक लाकडापासून बनवलेले हे लांबट आयताकृती आधारपात्र आहे. यात तीन छोट्या मेणबत्त्या ठेवता येतात.",
    },
    "Leaf-Shaped Wall Candle Holders (Set of 3)": {
        "hi": "पत्ती के आकार के वॉल कैंडल होल्डर (3 का सेट)",
        "mr": "पानांच्या आकारातील भिंतीवरील मेणबत्तीदानं (३ नग)",
    },
    "Three rustic wall-mounted candle holders shaped like leaves, each designed to hold one small candle.": {
        "hi": "पत्तियों के आकार के तीन देहाती शैली के वॉल कैंडल होल्डर। हर एक में एक छोटी मोमबत्ती रखी जा सकती है।",
        "mr": "साध्या ग्रामीण ढंगातील पानांच्या आकारातील मेणबत्तीदानं. प्रत्येक पात्र भिंतीवर लावता येते आणि त्यात एक छोटी मेणबत्ती ठेवता येते.",
    },
    "Painted Terracotta Candle Holders (Set of 3)": {
        "hi": "चित्रित टेराकोटा कैंडल होल्डर (3 का सेट)",
        "mr": "रंगवलेल्या मातीची मेणबत्तीदानं (३ नग)",
    },
    "Three red terracotta candle holders decorated with bold white geometric patterns.": {
        "hi": "गहरे सफेद ज्यामितीय पैटर्न से सजाए गए तीन लाल टेराकोटा कैंडल होल्डर।",
        "mr": "पांढऱ्या ठळक भौमितिक नक्षीने सजवलेली लाल मातीची मेणबत्तीदानं (३ नग).",
    },
}


class TranslationRequest(BaseModel):
    language: Literal["hi", "mr"]
    texts: list[str] = Field(min_length=1, max_length=100)


class TranslationResponse(BaseModel):
    translations: list[str]


def _translate_texts(texts: list[str], language: str) -> list[str]:
    return [
        _CURATED_PRODUCT_TRANSLATIONS.get(text, {}).get(language, text)
        for text in texts
    ]


def _enforce_rate_limit(client_id: str, character_count: int):
    now = time.monotonic()
    with _rate_limit_lock:
        requests = _translation_usage.setdefault(client_id, collections.deque())
        while requests and now - requests[0][0] >= 60:
            requests.popleft()

        request_count = len(requests)
        character_count_in_window = sum(characters for _, characters in requests)
        if (
            request_count >= MAX_REQUESTS_PER_MINUTE
            or character_count_in_window + character_count > MAX_CHARACTERS_PER_MINUTE
        ):
            raise HTTPException(status_code=429, detail="Translation request limit exceeded. Try again shortly.")
        requests.append((now, character_count))


@router.post("", response_model=TranslationResponse)
async def translate_texts(body: TranslationRequest, request: Request):
    if any(not text.strip() for text in body.texts):
        raise HTTPException(status_code=422, detail="Translation texts must not be empty.")
    if any(len(text) > MAX_TEXT_LENGTH for text in body.texts):
        raise HTTPException(status_code=422, detail="A translation text exceeds the maximum length.")
    if sum(len(text) for text in body.texts) > MAX_BATCH_CHARACTERS:
        raise HTTPException(status_code=422, detail="The translation batch exceeds the maximum size.")

    translations_by_text = {}
    with _translation_cache_lock:
        missing_texts = []
        for text in body.texts:
            cache_key = (body.language, text)
            if cache_key in _translation_cache:
                translations_by_text[text] = _translation_cache.pop(cache_key)
                _translation_cache[cache_key] = translations_by_text[text]
            elif text not in missing_texts:
                missing_texts.append(text)

    if missing_texts:
        client_id = request.client.host if request.client else "unknown"
        _enforce_rate_limit(client_id, sum(len(text) for text in missing_texts))
        translated_texts = _translate_texts(missing_texts, body.language)
        translations_by_text.update(zip(missing_texts, translated_texts))
        with _translation_cache_lock:
            for text, translated_text in zip(missing_texts, translated_texts):
                cache_key = (body.language, text)
                _translation_cache[cache_key] = translated_text
                while len(_translation_cache) > MAX_CACHED_TRANSLATIONS:
                    _translation_cache.popitem(last=False)

    translated_texts = [translations_by_text[text] for text in body.texts]
    return TranslationResponse(translations=translated_texts)
