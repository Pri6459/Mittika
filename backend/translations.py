import collections
import asyncio
import html
import json
import os
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request as URLRequest, urlopen

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from dotenv import load_dotenv

router = APIRouter(prefix="/translations", tags=["Translations"])
load_dotenv(Path(__file__).resolve().parent / ".env")
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
    "A statement necklace set with colorful Meenakari-inspired detailing, made to bring a festive touch to special occasions.": {
        "hi": "रंगीन मीनाकारी से सजा आकर्षक हार-सेट, जो खास मौकों पर उत्सवी रंग जोड़ता है।",
        "mr": "रंगीत मीनाकारीच्या नक्षीचा हा उठावदार हार-संच खास प्रसंगी उत्सवी रंग भरतो.",
    },
    "Classic hoop earrings with an antique silver look and handcrafted detailing for an easy traditional accent.": {
        "hi": "पुरानी चाँदी की छटा और हस्तनिर्मित बारीकियों वाले गोल झुमके, पारंपरिक अंदाज़ का सुंदर स्पर्श।",
        "mr": "पुरातन चांदीचा लुक आणि हस्तकलेच्या नक्षीची ही गोल कर्णभूषणे पारंपरिक लुकला उठाव देतात.",
    },
    "An oxidised-look necklace finished with playful tassels, pairing traditional character with a striking pop of color.": {
        "hi": "लटकनों से सजा ऑक्सिडाइज़्ड लुक वाला हार, पारंपरिक अंदाज़ के साथ रंगों का आकर्षक मेल।",
        "mr": "लटकनांनी सजवलेला ऑक्सिडाइझ्ड लुकचा हा हार पारंपरिक शैलीला रंगीत उठाव देतो.",
    },
    "A coordinated beaded necklace set inspired by bold tribal patterns and heritage craft.": {
        "hi": "जनजातीय नक्काशी और पारंपरिक शिल्प से प्रेरित मोतियों का आकर्षक हार-सेट।",
        "mr": "ठळक आदिवासी नक्षी आणि पारंपरिक हस्तकलेपासून प्रेरित मण्यांचा सुंदर हार-संच.",
    },
    "Lotus-inspired drop earrings accented with beads for a graceful finish to festive and everyday outfits.": {
        "hi": "कमल से प्रेरित और मोतियों से सजे लटकन झुमके, रोज़मर्रा और उत्सवी पहनावे के लिए।",
        "mr": "कमळाच्या आकारापासून प्रेरित, मण्यांनी सजवलेली ही झुलती कर्णभूषणे रोजच्या आणि सणाच्या पोशाखाला शोभतात.",
    },
    "A decorative necklace set featuring fabric rose motifs for a soft, handcrafted floral look.": {
        "hi": "कपड़े के गुलाबों वाला सजावटी हार-सेट, जो हस्तनिर्मित फूलों जैसा कोमल रूप देता है।",
        "mr": "कापडी गुलाबांच्या नक्षीचा हा सजावटी हार-संच हस्तनिर्मित फुलांचा नाजूक लुक देतो.",
    },
    "A bohemian-style set with cowrie shell accents, designed to add an earthy statement to relaxed looks.": {
        "hi": "कौड़ी के खोलों से सजा बोहेमियन सेट, आपके सहज अंदाज़ में मिट्टी की-सी खास पहचान जोड़ता है।",
        "mr": "कवड्यांच्या शिंपल्यांनी सजवलेला हा बोहेमियन संच साध्या पोशाखाला नैसर्गिक उठाव देतो.",
    },
    "A close-fitting choker with golden spiral and coin-inspired accents for a bold traditional silhouette.": {
        "hi": "सुनहरी घुमावदार और सिक्कों जैसी सजावट वाला गले से लगा चोकर, पारंपरिक अंदाज़ के लिए।",
        "mr": "सोनेरी वळणदार आणि नाण्यांच्या नक्षीचा गळ्यालगत बसणारा हा चोकर पारंपरिक लुकला उठाव देतो.",
    },
    "A handcrafted pearl necklace with a timeless, elegant look for celebrations or thoughtful gifting.": {
        "hi": "हस्तनिर्मित मोतियों का हार, उत्सवों या खास उपहार के लिए सदाबहार और सुरुचिपूर्ण विकल्प।",
        "mr": "हस्तनिर्मित मोत्यांचा हा हार समारंभासाठी किंवा खास भेट म्हणून शोभणारा, सदाबहार आणि देखणा पर्याय आहे.",
    },
    "Bridal earrings inspired by classic Kundan work, created to complement festive and wedding attire.": {
        "hi": "पारंपरिक कुंदन कला से प्रेरित दुल्हन के झुमके, शादी और उत्सवी पहनावे के साथ खूब जँचते हैं।",
        "mr": "पारंपरिक कुंदन कलेपासून प्रेरित ही वधूची कर्णभूषणे लग्नाच्या आणि सणाच्या पोशाखाला शोभतात.",
    },
    "Traditional-style Rajasthani lac bangles that bring vibrant color and folk-inspired charm to your look.": {
        "hi": "राजस्थानी लाख की पारंपरिक चूड़ियाँ, आपके रूप में चटख रंग और लोककला का आकर्षण जोड़ती हैं।",
        "mr": "राजस्थानी लाखेच्या पारंपरिक बांगड्या तुमच्या रूपाला उठावदार रंग आणि लोककलेचा साज देतात.",
    },
    "An oxidised-look necklace featuring a peacock-inspired design, celebrating the detail of Indian ornamentation.": {
        "hi": "मोर की आकृति वाला ऑक्सिडाइज़्ड लुक का हार, भारतीय आभूषण कला की बारीकियों को दर्शाता है।",
        "mr": "मोराच्या नक्षीचा ऑक्सिडाइझ्ड लुकचा हा हार भारतीय अलंकारकलेतील बारीक कामाचा सुंदर नमुना आहे.",
    },
    "Lightweight wooden jhumkas finished with hand-painted detail for a playful take on a familiar silhouette.": {
        "hi": "हाथ से रंगे हल्के लकड़ी के झुमके, पारंपरिक आकार को एक चंचल और नया रूप देते हैं।",
        "mr": "हाताने रंगवलेले हलके लाकडी झुमके पारंपरिक आकाराला नवा आणि खेळकर लुक देतात.",
    },
    "A silver-look pendant with delicate filigree-inspired openwork for an understated handcrafted accent.": {
        "hi": "नाज़ुक जालीदार नक्काशी वाला चाँदी-सा पेंडेंट, सादगी में हस्तकला का सुंदर स्पर्श।",
        "mr": "नाजूक जाळीदार नक्षीचा चांदीसारखा हा पेंडंट साध्या लुकला हस्तकलेचा देखणा स्पर्श देतो.",
    },
    "A terracotta necklace decorated with bell charms, combining earthy character with a gentle festive feel.": {
        "hi": "घंटी जैसे आकर्षणों से सजा टेराकोटा हार, मिट्टी की सादगी और उत्सवी लुक का सुंदर मेल।",
        "mr": "घुंगरांच्या लटकनांनी सजवलेला मातीचा हा हार नैसर्गिक साधेपणा आणि उत्सवी थाट यांचा सुंदर संगम आहे.",
    },
    "A coordinated bangle set with colorful enamel-inspired decoration to brighten traditional outfits.": {
        "hi": "रंगीन मीनाकारी जैसी सजावट वाला चूड़ियों का सेट, पारंपरिक पहनावे में रौनक जोड़ने के लिए।",
        "mr": "रंगीत मीनाकारीसारख्या नक्षीचा हा बांगड्यांचा संच पारंपरिक पोशाखात रंग भरतो.",
    },
    "A distinctive necklace centered on an elephant-head motif, with golden tones inspired by traditional adornment.": {
        "hi": "हाथी के सिर की आकृति वाला खास हार, पारंपरिक आभूषणों से प्रेरित सुनहरी छटा के साथ।",
        "mr": "हत्तीच्या मुखाच्या नक्षीचा हा खास हार पारंपरिक अलंकारांपासून प्रेरित सोनेरी रंगछटांनी सजला आहे.",
    },
    "Compact stud earrings with mirror-work-inspired accents that catch the light and add a festive touch.": {
        "hi": "शीशे की कारीगरी जैसी चमक वाले छोटे स्टड झुमके, जो रोशनी में दमकते और उत्सवी रंग जोड़ते हैं।",
        "mr": "आरशाच्या कामासारखी चमक असलेले हे छोटे स्टड कानातले प्रकाशात चमकतात आणि उत्सवी लुक देतात.",
    },
    "A temple-style necklace inspired by traditional Indian motifs, suited to celebrations and cultural occasions.": {
        "hi": "पारंपरिक भारतीय आकृतियों से प्रेरित मंदिर-शैली का हार, उत्सवों और सांस्कृतिक अवसरों के लिए।",
        "mr": "पारंपरिक भारतीय नक्षींनी प्रेरित मंदिर-शैलीचा हा हार सण आणि सांस्कृतिक प्रसंगांसाठी योग्य आहे.",
    },
    "A set of nose pins with an oxidised finish, offering a small but distinctive traditional accent.": {
        "hi": "ऑक्सिडाइज़्ड फिनिश वाली नथों का सेट, पारंपरिक अंदाज़ का छोटा लेकिन खास स्पर्श।",
        "mr": "ऑक्सिडाइझ्ड फिनिशच्या नथांचा हा संच पारंपरिक लुकला छोटासा पण खास उठाव देतो.",
    },
    "Brass earrings shaped by tribal-inspired styling, bringing a bold artisanal detail to your ensemble.": {
        "hi": "जनजातीय शैली से प्रेरित पीतल के झुमके, आपके पहनावे में शिल्पकला का दमदार स्पर्श जोड़ते हैं।",
        "mr": "आदिवासी शैलीपासून प्रेरित पितळी कर्णभूषणे तुमच्या पोशाखाला हस्तकलेचा ठळक उठाव देतात.",
    },
    "A crystal-accented drop pendant with a simple, luminous design for both special occasions and gifting.": {
        "hi": "क्रिस्टल की चमक वाला लटकन पेंडेंट, खास मौकों और उपहार देने के लिए सादगी भरा सुंदर डिज़ाइन।",
        "mr": "क्रिस्टलच्या चमकदार नक्षीचा हा लटकन पेंडंट खास प्रसंगांसाठी आणि भेट देण्यासाठी सुंदर आहे.",
    },
    "A kada bracelet with an antique silver look, adding a substantial traditional accent to the wrist.": {
        "hi": "पुरानी चाँदी की छटा वाला कड़ा, कलाई को पारंपरिक और दमदार रूप देता है।",
        "mr": "पुरातन चांदीचा लुक असलेले हे कडे मनगटाला पारंपरिक आणि उठावदार रूप देते.",
    },
    "A necklace built around handwoven thread, with a colorful, relaxed style rooted in craft.": {
        "hi": "हाथ से बुने धागों का रंगीन हार, शिल्पकला से जुड़ा सहज और आकर्षक अंदाज़।",
        "mr": "हाताने विणलेल्या धाग्यांचा हा रंगीत हार हस्तकलेचा सहज आणि सुंदर लुक देतो.",
    },
    "A bridal jewellery set inspired by Polki design, made to bring a graceful statement to wedding attire.": {
        "hi": "पोल्की डिज़ाइन से प्रेरित दुल्हन का आभूषण सेट, शादी के पहनावे को गरिमामय आकर्षण देता है।",
        "mr": "पोल्की नक्षीपासून प्रेरित वधूचा हा दागिन्यांचा संच लग्नाच्या पोशाखाला देखणा उठाव देतो.",
    },
    "Handcrafted wooden earrings with a natural, lightweight feel and a distinctive artisan finish.": {
        "hi": "प्राकृतिक रूप और अनोखी कारीगरी वाले हस्तनिर्मित लकड़ी के हल्के झुमके।",
        "mr": "नैसर्गिक लुक आणि वेगळ्या हस्तकलेची झलक असलेले हे हलके लाकडी कानातले हाताने बनवले आहेत.",
    },
    "A set of bangles combining beadwork and mirror-inspired accents for a lively festive look.": {
        "hi": "मोतियों और शीशे जैसी सजावट वाली चूड़ियों का सेट, उत्सवी पहनावे में नई रौनक के लिए।",
        "mr": "मणी आणि आरशासारख्या सजावटीचा हा बांगड्यांचा संच सणाच्या पोशाखात रंगत आणतो.",
    },
    "A decorative hair pin accented with pearls, adding a delicate finishing touch to styled hair.": {
        "hi": "मोती से सजी सजावटी हेयर पिन, संवारे हुए बालों को नाज़ुक और सुंदर अंतिम स्पर्श देती है।",
        "mr": "मोत्यांनी सजवलेली ही हेअरपिन केशरचनेला नाजूक आणि देखणा अंतिम स्पर्श देते.",
    },
    "Toe rings with engraved stone-inspired detail, offering a subtle traditional accent for everyday wear.": {
        "hi": "पत्थर जैसी नक्काशी वाले बिछुए, रोज़मर्रा के पहनावे में पारंपरिक अंदाज़ का हल्का स्पर्श।",
        "mr": "खड्याच्या नक्षीसारखे कोरीव काम असलेली ही जोडवी रोजच्या वापराला पारंपरिक साज देतात.",
    },
    "A Kundan-inspired maang tikka designed as a graceful centerpiece for bridal and festive styling.": {
        "hi": "कुंदन कला से प्रेरित मांग टीका, दुल्हन और उत्सवी श्रृंगार का सुंदर केंद्रबिंदु।",
        "mr": "कुंदन कलेपासून प्रेरित हा मांगटिळा वधूच्या आणि सणाच्या शृंगाराचा देखणा केंद्रबिंदू ठरतो.",
    },
    "A festive platter dressed with colorful hand-finished details, ready to display or present as a thoughtful gift.": {
        "hi": "रंगीन हाथ की सजावट वाली उत्सवी थाली, सजाने या खास उपहार के रूप में देने के लिए।",
        "mr": "रंगीत हस्तकलेने सजवलेली ही उत्सवी थाळी सजावटीसाठी किंवा खास भेट म्हणून देण्यासाठी योग्य आहे.",
    },
    "A miniature kitchen collection painted by hand, capturing the charm of traditional household scenes in a keepsake display.": {
        "hi": "हाथ से रंगा छोटा रसोई-संग्रह, पारंपरिक घरेलू जीवन की झलक को यादगार सजावट में संजोता है।",
        "mr": "हाताने रंगवलेला हा छोटेखानी स्वयंपाकघराचा संच पारंपरिक घरगुती जीवनाची झलक आठवणीत जपतो.",
    },
    "Four whimsical birdhouses decorated with pistachio shells, bringing a playful natural texture to a festive display.": {
        "hi": "पिस्ते के छिलकों से सजे चार सुंदर पक्षीघर, उत्सवी सजावट में प्राकृतिक बनावट और चंचलता जोड़ते हैं।",
        "mr": "पिस्त्याच्या टरफलांनी सजवलेली ही चार पक्ष्यांची घरटी उत्सवी सजावटीत नैसर्गिक पोत आणि खेळकरपणा आणतात.",
    },
    "A set of five small wooden trays finished with patterned fabric, made for decorative presentation and serving.": {
        "hi": "पैटर्न वाले कपड़े से सजी पाँच छोटी लकड़ी की ट्रे, सजावट और परोसने के लिए उपयोगी।",
        "mr": "नक्षीदार कापडाने सजवलेल्या पाच छोट्या लाकडी ट्रे सजावटीसाठी आणि पदार्थ वाढण्यासाठी उपयोगी आहेत.",
    },
    "A miniature collection of musical instruments arranged as a decorative tribute to India's rich musical traditions.": {
        "hi": "भारत की समृद्ध संगीत परंपरा को समर्पित, सजावट के लिए सजे छोटे वाद्ययंत्रों का संग्रह।",
        "mr": "भारताच्या समृद्ध संगीतपरंपरेला समर्पित, सजावटीसाठी मांडलेल्या छोट्या वाद्यांचा हा संच आहे.",
    },
    "A finely arranged miniature instrument set that makes a distinctive display piece for music lovers and festive décor.": {
        "hi": "बारीकी से सजा छोटा वाद्य-संग्रह, संगीत प्रेमियों और उत्सवी सजावट के लिए खास शोपीस।",
        "mr": "सुंदर मांडणीचा हा छोटेखानी वाद्यसंच संगीतप्रेमींसाठी आणि उत्सवी सजावटीसाठी खास शोभेची वस्तू आहे.",
    },
    "A hand-painted plate inspired by Marathi wedding traditions, created to bring regional color to a Rukhwat display.": {
        "hi": "मराठी विवाह परंपराओं से प्रेरित हाथ से रंगी थाली, रुखवत सजावट में क्षेत्रीय रंग जोड़ने के लिए।",
        "mr": "मराठी विवाहपरंपरेपासून प्रेरित हाताने रंगवलेली ही थाळी रुखवत सजावटीत प्रादेशिक रंग भरते.",
    },
    "A decorative wedding thali finished with hand-painted details for ceremonies, gifting, or a traditional home display.": {
        "hi": "हाथ से रंगी सजावटी विवाह थाली, समारोह, उपहार या पारंपरिक घरेलू सजावट के लिए।",
        "mr": "हाताने रंगवलेली सजावटी लग्नाची थाळी समारंभ, भेट किंवा पारंपरिक घरसजावटीसाठी योग्य आहे.",
    },
    "A miniature house assembled from craft sticks, turning simple materials into a charming handmade display.": {
        "hi": "हस्तकला की लकड़ियों से बना छोटा घर, साधारण सामग्री को आकर्षक हस्तनिर्मित सजावट में बदलता है।",
        "mr": "क्राफ्टच्या काड्यांपासून बनवलेले हे छोटे घर साध्या साहित्याचे आकर्षक हस्तनिर्मित सजावटीत रूपांतर करते.",
    },
    "A decorative pair of cones for bridal and groom displays, adding a traditional finishing touch to wedding décor.": {
        "hi": "दूल्हा-दुल्हन की सजावट के लिए शंकुओं की जोड़ी, विवाह सज्जा को पारंपरिक अंतिम स्पर्श देती है।",
        "mr": "वधू-वराच्या सजावटीसाठी शंकूंची ही जोडी लग्नाच्या सजावटीला पारंपरिक पूर्णत्व देते.",
    },
    "Four small silk-look gift bags designed for miniature displays, festive favors, or decorative presentation.": {
        "hi": "रेशमी रूप वाले चार छोटे उपहार बैग, छोटी सजावट, उत्सवी भेंट या सुंदर प्रस्तुति के लिए।",
        "mr": "रेशमी लुकच्या या चार छोट्या पिशव्या छोट्या सजावटीसाठी, सणाच्या भेटींसाठी किंवा आकर्षक मांडणीसाठी आहेत.",
    },
    "Handmade miniature paper dolls dressed in traditional attire, celebrating folk style in a compact keepsake display.": {
        "hi": "पारंपरिक वेशभूषा वाली हस्तनिर्मित छोटी कागज़ की गुड़िया, लोकशैली की सुंदर यादगार सजावट।",
        "mr": "पारंपरिक वेशभूषेतील हाताने बनवलेल्या छोट्या कागदी बाहुल्या लोकशैलीची सुंदर आठवण जपतात.",
    },
    "A small wedding ceremony thali arranged for miniature Rukhwat displays and traditional festive decoration.": {
        "hi": "छोटी विवाह-समारोह थाली, लघु रुखवत प्रदर्शन और पारंपरिक उत्सवी सजावट के लिए।",
        "mr": "छोटेखानी लग्नसमारंभाची ही थाळी लघुरूप रुखवत मांडणी आणि पारंपरिक उत्सवी सजावटीसाठी आहे.",
    },
    "A traditional winnowing basket styled with wheat, representing harvest and abundance in a festive display.": {
        "hi": "गेहूँ से सजी पारंपरिक सूप की टोकरी, उत्सवी सजावट में फसल और समृद्धि का प्रतीक।",
        "mr": "गव्हाने सजवलेले पारंपरिक सुप उत्सवी मांडणीत पीक आणि समृद्धीचे प्रतीक ठरते.",
    },
    "A generously sized decorative basket for arranging wedding keepsakes and celebrating the custom of Rukhwat.": {
        "hi": "विवाह की यादगार वस्तुएँ सजाने और रुखवत परंपरा मनाने के लिए बड़ी सजावटी टोकरी।",
        "mr": "लग्नाच्या आठवणींच्या वस्तू मांडण्यासाठी आणि रुखवत परंपरा साजरी करण्यासाठी मोठी सजावटी टोपली.",
    },
    "A miniature Tulsi Vivah arrangement that brings the beloved ceremonial tradition into a detailed decorative keepsake.": {
        "hi": "तुलसी विवाह की छोटी सजावट, इस प्रिय धार्मिक परंपरा को बारीकियों वाली यादगार कलाकृति में संजोती है।",
        "mr": "तुळशीविवाहाची ही छोटी सजावट प्रिय धार्मिक परंपरेची आठवण कलाकुसरीच्या रूपात जपते.",
    },
    "A colorful hand-painted plate made to honor Marathi wedding customs and complete a traditional Rukhwat arrangement.": {
        "hi": "मराठी विवाह रीति-रिवाज़ों के सम्मान में रंगी हाथ की थाली, पारंपरिक रुखवत सजावट को पूरा करती है।",
        "mr": "मराठी विवाहरीतींचा सन्मान करणारी हाताने रंगवलेली रंगीत थाळी पारंपरिक रुखवत मांडणी पूर्ण करते.",
    },
    "A hand-painted thali with a festive presence, suitable for wedding ceremonies, gifting, and cultural displays.": {
        "hi": "उत्सवी रूप वाली हाथ से रंगी थाली, विवाह समारोह, उपहार और सांस्कृतिक सजावट के लिए उपयुक्त।",
        "mr": "उत्सवी रूपाची हाताने रंगवलेली थाळी लग्नसमारंभ, भेटवस्तू आणि सांस्कृतिक सजावटीसाठी योग्य आहे.",
    },
    "A handcrafted miniature house made from craft sticks, adding a cheerful handmade accent to a celebration display.": {
        "hi": "हस्तकला की लकड़ियों से बना छोटा घर, उत्सवी सजावट में हस्तनिर्मित खुशमिज़ाज रंग जोड़ता है।",
        "mr": "क्राफ्टच्या काड्यांपासून बनवलेले छोटे घर उत्सवी मांडणीत आनंदी हस्तनिर्मित साज आणते.",
    },
    "A matching set of decorative bridal and groom cones for traditional wedding arrangements and keepsake displays.": {
        "hi": "पारंपरिक विवाह सजावट और यादगार प्रदर्शन के लिए दूल्हा-दुल्हन के शंकुओं का मेल खाता सेट।",
        "mr": "पारंपरिक लग्नाची मांडणी आणि आठवणींच्या सजावटीसाठी वधू-वरांच्या शंकूंचा जुळता संच.",
    },
    "A set of four miniature gift bags with a silk-inspired finish, perfect for festive styling and tiny keepsakes.": {
        "hi": "रेशमी फिनिश वाले चार छोटे उपहार बैग, उत्सवी सजावट और छोटी यादगार वस्तुओं के लिए।",
        "mr": "रेशमी फिनिशच्या या चार छोट्या पिशव्या सणाच्या सजावटीसाठी आणि छोट्या आठवणींसाठी सुंदर आहेत.",
    },
    "Traditional attire and handmade detail give these miniature paper dolls a charming place in a cultural display.": {
        "hi": "पारंपरिक वेशभूषा और हस्तनिर्मित बारीकियाँ इन छोटी कागज़ की गुड़ियों को सांस्कृतिक सजावट में खास बनाती हैं।",
        "mr": "पारंपरिक वेशभूषा आणि हस्तकलेच्या नक्षीमुळे या छोट्या कागदी बाहुल्या सांस्कृतिक मांडणीत उठून दिसतात.",
    },
    "A miniature thali for wedding-themed displays, thoughtfully styled to evoke the rituals of a traditional celebration.": {
        "hi": "विवाह-थीम वाली सजावट के लिए छोटी थाली, पारंपरिक समारोह की रस्मों की याद दिलाती है।",
        "mr": "लग्नविषयक सजावटीसाठीची ही छोटी थाळी पारंपरिक समारंभातील विधींची आठवण करून देते.",
    },
    "A decorative wheat-filled winnowing basket that brings a harvest-inspired touch to wedding and festive décor.": {
        "hi": "गेहूँ से भरा सजावटी सूप, विवाह और उत्सवी सजावट में फसल की परंपरा का स्पर्श जोड़ता है।",
        "mr": "गव्हाने भरलेले सजावटी सुप लग्नाच्या आणि सणाच्या सजावटीत कापणीपरंपरेचा साज आणते.",
    },
    "A large showcase basket designed to hold wedding display pieces and add a traditional focal point to the occasion.": {
        "hi": "विवाह की सजावटी वस्तुएँ रखने और अवसर को पारंपरिक आकर्षण देने के लिए बड़ी प्रदर्शन टोकरी।",
        "mr": "लग्नाच्या सजावटीच्या वस्तू ठेवण्यासाठी आणि प्रसंगाला पारंपरिक उठाव देण्यासाठी मोठी मांडणीची टोपली.",
    },
    "A detailed miniature set inspired by Tulsi Vivah, bringing a meaningful ceremonial scene to your home décor.": {
        "hi": "तुलसी विवाह से प्रेरित बारीकियों वाला छोटा सेट, घर की सजावट में एक अर्थपूर्ण धार्मिक दृश्य जोड़ता है।",
        "mr": "तुळशीविवाहापासून प्रेरित तपशीलवार छोटा संच घरसजावटीत अर्थपूर्ण धार्मिक दृश्य साकारतो.",
    },
    "Earthy terracotta chimes bring gentle movement and a warm, handmade accent to a balcony, window, or garden.": {
        "hi": "मिट्टी के टेराकोटा विंड चाइम बालकनी, खिड़की या बगीचे में हल्की धुन और हस्तनिर्मित गर्माहट जोड़ते हैं।",
        "mr": "मातीच्या टेराकोटा विंड चाइम्स बाल्कनी, खिडकी किंवा बागेत मंद नाद आणि हस्तकलेची ऊब आणतात.",
    },
    "A terracotta planter decorated with traditional motifs, ready to display a favorite plant indoors or outside.": {
        "hi": "पारंपरिक आकृतियों से सजा टेराकोटा गमला, घर के भीतर या बाहर पसंदीदा पौधा रखने के लिए।",
        "mr": "पारंपरिक नक्षीने सजवलेली मातीची कुंडी घरात किंवा बाहेर आवडते रोप लावण्यासाठी योग्य आहे.",
    },
    "A glass bottle transformed into a decorative accent, adding handcrafted character to a shelf or tabletop.": {
        "hi": "सजावटी रूप में बदली काँच की बोतल, शेल्फ या मेज़ पर हस्तकला का आकर्षण जोड़ती है।",
        "mr": "सजावटी वस्तूत रूपांतरित केलेली काचेची बाटली शेल्फ किंवा टेबलाला हस्तकलेचा साज देते.",
    },
    "A ceramic countertop holder that keeps cooking utensils together while adding an artful touch to the kitchen.": {
        "hi": "रसोई के बर्तनों को साथ रखने वाला सिरेमिक होल्डर, काउंटर पर कलात्मक स्पर्श भी जोड़ता है।",
        "mr": "स्वयंपाकाची साधने एकत्र ठेवणारा हा सिरॅमिक होल्डर स्वयंपाकघराच्या ओट्याला कलात्मक साजही देतो.",
    },
    "A storage pot finished with hand-painted decoration, combining practical use with the warmth of artisan craft.": {
        "hi": "हाथ से रंगी सजावट वाला भंडारण पात्र, उपयोगिता और कारीगरी की गर्माहट का सुंदर मेल।",
        "mr": "हाताने रंगवलेली सजावट असलेले हे साठवणीचे भांडे उपयोगिता आणि हस्तकलेची ऊब एकत्र आणते.",
    },
    "A ceramic vase featuring elephant-inspired detailing, designed to stand out with flowers or as a display piece.": {
        "hi": "हाथी से प्रेरित बारीकियों वाला सिरेमिक फूलदान, फूलों के साथ या अकेले सजावट में सुंदर लगता है।",
        "mr": "हत्तीच्या नक्षीचे सिरॅमिक फुलदाणी फुलांसह किंवा स्वतंत्र सजावटीची वस्तू म्हणून शोभून दिसते.",
    },
    "A petite decorative jar for storing small keepsakes or adding a handcrafted accent to a shelf.": {
        "hi": "छोटी यादगार वस्तुएँ रखने या शेल्फ पर हस्तनिर्मित सजावट जोड़ने के लिए नन्हा सजावटी जार।",
        "mr": "छोट्या आठवणींच्या वस्तू ठेवण्यासाठी किंवा शेल्फला हस्तकलेचा साज देण्यासाठी छोटी सजावटी बरणी.",
    },
    "A terracotta lantern with a warm, earthy presence, bringing a welcoming glow to a quiet corner or celebration.": {
        "hi": "मिट्टी की गर्माहट वाला टेराकोटा लालटेन, शांत कोने या उत्सव में स्वागत भरी रोशनी लाता है।",
        "mr": "मातीची ऊब असलेला टेराकोटा कंदील शांत कोपऱ्यात किंवा उत्सवात प्रसन्न प्रकाश देतो.",
    },
    "A statement vase with contrasting black-and-white painted decoration for contemporary or traditional interiors.": {
        "hi": "काले-सफेद रंग की विपरीत चित्रकारी वाला आकर्षक फूलदान, आधुनिक या पारंपरिक घरों के लिए।",
        "mr": "काळ्या-पांढऱ्या रंगांच्या उठावदार चित्रकामाची ही फुलदाणी आधुनिक किंवा पारंपरिक घरसजावटीला शोभते.",
    },
    "A stacked-pot arrangement in a rich red tone, offering a sculptural focal point for indoor or outdoor spaces.": {
        "hi": "गहरे लाल रंग में गमलों की सजावटी परतदार रचना, भीतर या बाहर की जगह का खास आकर्षण।",
        "mr": "गडद लाल रंगातील एकावर एक रचलेल्या कुंड्यांची सजावट घरातील किंवा बाहेरील जागेचा उठावदार केंद्रबिंदू ठरते.",
    },
    "A traditional clay jug highlighted with carved details, celebrating the texture and form of earthenware.": {
        "hi": "नक्काशीदार बारीकियों वाला पारंपरिक मिट्टी का घड़ा, मृद्भांड की बनावट और आकार का उत्सव।",
        "mr": "कोरीव नक्षीने उठाव दिलेला पारंपरिक मातीचा घडा मृद्भांडाचा पोत आणि आकार सुंदरपणे दाखवतो.",
    },
    "A leaf-inspired wall hanging that brings a nature-led shape and handmade detail to your wall décor.": {
        "hi": "पत्ते से प्रेरित दीवार सजावट, दीवार पर प्रकृति का आकार और हस्तनिर्मित बारीकी जोड़ती है।",
        "mr": "पानाच्या आकारापासून प्रेरित ही भिंतीवरील सजावट निसर्गाचा आकार आणि हस्तकलेचा तपशील आणते.",
    },
    "Four wooden bowls with natural character, suited to serving, arranging small items, or styling a tabletop.": {
        "hi": "प्राकृतिक रूप वाले चार लकड़ी के कटोरे, परोसने, छोटी वस्तुएँ रखने या मेज़ सजाने के लिए।",
        "mr": "नैसर्गिक लुकचे चार लाकडी बाऊल पदार्थ वाढण्यासाठी, छोट्या वस्तू ठेवण्यासाठी किंवा टेबल सजवण्यासाठी उपयोगी आहेत.",
    },
    "A coordinated set of four decorative plates for creating a colorful arrangement on a wall or display shelf.": {
        "hi": "दीवार या शेल्फ पर रंगीन सजावट बनाने के लिए सजावटी प्लेटों का मेल खाता सेट।",
        "mr": "भिंतीवर किंवा शेल्फवर रंगीत सजावट करण्यासाठी सजावटी प्लेट्सचा हा जुळता संच आहे.",
    },
    "A vase decorated with a blue elephant motif, bringing folk-inspired color to flowers or a display shelf.": {
        "hi": "नीले हाथी की आकृति से सजा फूलदान, फूलों या सजावटी शेल्फ में लोककला के रंग जोड़ता है।",
        "mr": "निळ्या हत्तीच्या नक्षीची ही फुलदाणी फुलांसह किंवा सजावटीच्या शेल्फवर लोककलेचे रंग आणते.",
    },
    "A classic terracotta diya for a warm, traditional glow during daily prayers and festive gatherings.": {
        "hi": "रोज़ की पूजा और उत्सवों में पारंपरिक गर्म रोशनी देने वाला क्लासिक टेराकोटा दीया।",
        "mr": "दैनंदिन पूजा आणि सणांच्या वेळी पारंपरिक उबदार प्रकाश देणारा मातीचा दिवा.",
    },
    "A terracotta bell-style chime with an earthy handmade look, adding a gentle accent to open spaces.": {
        "hi": "मिट्टी के हस्तनिर्मित रूप वाला घंटी-शैली का टेराकोटा चाइम, खुली जगहों में मधुर सजावट जोड़ता है।",
        "mr": "मातीच्या हस्तनिर्मित लुकचा घंटेसारखा टेराकोटा चाइम मोकळ्या जागेला हलका सजावटी साज देतो.",
    },
    "A pair of camel-shaped planters that bring a playful folk-art touch to small plants and succulents.": {
        "hi": "ऊँट के आकार के दो गमले, छोटे पौधों और सक्यूलेंट्स में लोककला का चंचल स्पर्श जोड़ते हैं।",
        "mr": "उंटाच्या आकाराच्या या दोन कुंड्या छोट्या रोपांना आणि सक्युलंट्सना लोककलेचा खेळकर साज देतात.",
    },
    "An abstract ceramic vase with an expressive silhouette, made to complement blooms or stand alone as art.": {
        "hi": "अनोखे आकार वाला अमूर्त सिरेमिक फूलदान, फूलों के साथ या स्वतंत्र कलाकृति की तरह सुंदर।",
        "mr": "वेगळ्या आकाराची अमूर्त सिरॅमिक फुलदाणी फुलांसह किंवा स्वतंत्र कलाकृती म्हणून शोभते.",
    },
    "Three characterful humanoid figurines arranged as a sculptural set for shelves, desks, or curated displays.": {
        "hi": "अनोखे रूप वाली तीन मानवाकार मूर्तियाँ, शेल्फ, मेज़ या चुनी हुई सजावट के लिए एक कलात्मक सेट।",
        "mr": "वेगळ्या रूपाच्या तीन मानवाकृती मूर्ती शेल्फ, टेबल किंवा खास सजावटीसाठी शिल्पसंच म्हणून मांडता येतात.",
    },
    "Two hand-painted figurine planters that pair functional planting space with cheerful sculptural detail.": {
        "hi": "हाथ से रंगे दो मूर्ति-आकार के गमले, पौधे लगाने की जगह और खुशमिज़ाज कलात्मक रूप का मेल।",
        "mr": "हाताने रंगवलेल्या दोन मूर्तीरूप कुंड्या रोपांसाठी जागा आणि आनंदी शिल्पकला यांचा मेळ घालतात.",
    },
    "A large terracotta planter shaped around an elephant motif, bringing folk-inspired character to a favorite plant.": {
        "hi": "हाथी की आकृति वाला बड़ा टेराकोटा गमला, पसंदीदा पौधे में लोककला का अनोखा रूप जोड़ता है।",
        "mr": "हत्तीच्या नक्षीची मोठी मातीची कुंडी आवडत्या रोपाला लोककलेचा वेगळा साज देते.",
    },
    "A handmade ceramic tic-tac-toe set that turns a familiar game into a playful keepsake for the home.": {
        "hi": "हस्तनिर्मित सिरेमिक टिक-टैक-टो सेट, जाने-पहचाने खेल को घर के लिए मज़ेदार यादगार बनाता है।",
        "mr": "हाताने बनवलेला सिरॅमिक टिक-टॅक-टो संच परिचित खेळाला घरासाठी खेळकर आठवण बनवतो.",
    },
    "A relaxed sloth design makes this ceramic incense holder a charming addition to a calm corner.": {
        "hi": "सुस्त स्लॉथ का रूप इस सिरेमिक अगरबत्ती स्टैंड को शांत कोने की आकर्षक सजावट बनाता है।",
        "mr": "निवांत स्लॉथची रचना या सिरॅमिक अगरबत्ती पात्राला शांत कोपऱ्यातील आकर्षक सजावट बनवते.",
    },
    "A miniature terracotta kitchen set that captures the charm of traditional earthenware in a decorative display.": {
        "hi": "टेराकोटा का छोटा रसोई सेट, सजावटी रूप में पारंपरिक मिट्टी के बर्तनों का आकर्षण समेटे हुए।",
        "mr": "टेराकोटाचा छोटा स्वयंपाकघर संच सजावटी मांडणीत पारंपरिक मातीच्या भांड्यांचा साज जपतो.",
    },
    "A whimsical mushroom-shaped holder keeps brushes together while adding a playful handmade detail to a desk.": {
        "hi": "मशरूम के आकार का मज़ेदार होल्डर ब्रश साथ रखता है और मेज़ पर हस्तनिर्मित चंचलता जोड़ता है।",
        "mr": "मशरूमच्या आकाराचे हे मजेशीर पात्र ब्रश एकत्र ठेवते आणि टेबलाला हस्तकलेचा खेळकर साज देते.",
    },
    "A handmade earthenware money bank offers a simple place to save and a charming accent for a shelf.": {
        "hi": "हस्तनिर्मित मिट्टी की गुल्लक बचत के लिए सरल जगह और शेल्फ के लिए सुंदर सजावट देती है।",
        "mr": "हाताने बनवलेली मातीची बचतपेटी पैसे साठवण्यासाठी सोयीची आणि शेल्फसाठी देखणी सजावट आहे.",
    },
    "Four hanging terracotta planters create a warm, layered display for trailing plants on a balcony or patio.": {
        "hi": "चार लटकते टेराकोटा गमले बालकनी या आँगन में लटकते पौधों की सुंदर, गर्माहट भरी सजावट बनाते हैं।",
        "mr": "चार टांगत्या मातीच्या कुंड्या बाल्कनी किंवा अंगणात वेलवर्गीय रोपांची उबदार, थरदार सजावट करतात.",
    },
    "A set of miniature divine figurines for a home shrine, prayer space, or thoughtful spiritual gift.": {
        "hi": "घर के मंदिर, पूजा स्थान या आध्यात्मिक उपहार के लिए छोटी दिव्य मूर्तियों का सेट।",
        "mr": "घरातील देवघर, पूजास्थान किंवा आध्यात्मिक भेटीसाठी छोट्या दिव्य मूर्तींचा संच.",
    },
    "A devotional tea light holder featuring Lakshmi and Ganesha, made to bring a warm glow to festive prayers.": {
        "hi": "लक्ष्मी और गणेश की आकृति वाला पूजा टी-लाइट होल्डर, उत्सवी आरती में गर्म रोशनी भरता है।",
        "mr": "लक्ष्मी आणि गणेशाच्या प्रतिमेचा हा पूजेसाठीचा टी-लाइट होल्डर सणाच्या आरतीत उबदार प्रकाश देतो.",
    },
    "A terracotta lamp stand with a devotional design, bringing an earthy handmade presence to your puja space.": {
        "hi": "भक्ति-भाव वाली आकृति का टेराकोटा दीप-स्टैंड, पूजा स्थान में मिट्टी की हस्तनिर्मित सुंदरता लाता है।",
        "mr": "भक्तिपूर्ण नक्षीचा मातीचा दिवा-स्टँड पूजास्थानाला हस्तकलेचा नैसर्गिक साज देतो.",
    },
    "A handcrafted incense burner made from coconut shell, offering a natural-looking accent for moments of reflection.": {
        "hi": "नारियल के खोल से बना हस्तनिर्मित धूपदान, ध्यान और मनन के क्षणों के लिए प्राकृतिक सजावट।",
        "mr": "नारळाच्या करवंटीपासून बनवलेले हस्तनिर्मित धूपपात्र चिंतनाच्या क्षणांना नैसर्गिक साज देते.",
    },
    "A miniature temple-inspired replica that makes a meaningful decorative piece for a shelf or prayer corner.": {
        "hi": "मंदिर से प्रेरित छोटी प्रतिकृति, शेल्फ या पूजा कोने के लिए अर्थपूर्ण सजावटी वस्तु।",
        "mr": "मंदिरापासून प्रेरित छोटी प्रतिकृती शेल्फ किंवा पूजेच्या कोपऱ्यासाठी अर्थपूर्ण सजावटी वस्तू आहे.",
    },
    "An elephant wall accent decorated with mirror-mosaic detail, adding sparkle and a traditional motif to your space.": {
        "hi": "शीशे की मोज़ेक सजावट वाला हाथी दीवार-अलंकरण, घर में चमक और पारंपरिक आकृति जोड़ता है।",
        "mr": "आरशाच्या मोझॅक नक्षीचा हत्तीच्या आकारातील भिंतीवरील सजावटीचा हा भाग घराला चमक आणि पारंपरिक साज देतो.",
    },
    "A hand-knitted lotus-inspired outfit made to dress a Krishna figurine for worship or festive display.": {
        "hi": "कृष्ण की मूर्ति को सजाने के लिए हाथ से बुनी कमल-प्रेरित पोशाक, पूजा या उत्सवी प्रदर्शन हेतु।",
        "mr": "कृष्णमूर्तीला परिधान करण्यासाठी हाताने विणलेला कमळाच्या आकाराचा पोशाख, पूजा किंवा सणाच्या सजावटीसाठी.",
    },
    "A hand-knitted garland in white and red floral tones for decorating a home shrine or festive setting.": {
        "hi": "सफेद और लाल फूलों के रंगों वाली हाथ से बुनी माला, मंदिर या उत्सवी सजावट के लिए।",
        "mr": "पांढऱ्या आणि लाल फुलांच्या रंगछटांची हाताने विणलेली माळ देवघर किंवा सणाच्या सजावटीसाठी.",
    },
    "A 250 ml bottle of Ganga Jal for personal worship and customary religious rituals.": {
        "hi": "व्यक्तिगत पूजा और पारंपरिक धार्मिक अनुष्ठानों के लिए गंगाजल की 250 मिलीलीटर बोतल।",
        "mr": "वैयक्तिक पूजा आणि पारंपरिक धार्मिक विधींसाठी गंगाजलाची २५० मिली बाटली.",
    },
    "A coordinated puja kit prepared for Karwa Chauth observances and the rituals of the festive evening.": {
        "hi": "करवा चौथ व्रत और त्योहार की शाम की रस्मों के लिए तैयार पूजा सामग्री का पूरा सेट।",
        "mr": "करवा चौथ व्रत आणि सणाच्या संध्याकाळच्या विधींसाठी तयार केलेला पूजासाहित्याचा संपूर्ण संच.",
    },
    "A hand-carved wooden Buddha head with a contemplative presence, suited to a quiet space for rest or reflection.": {
        "hi": "शांत चिंतन के लिए उपयुक्त, मननशील रूप वाला हाथ से तराशा हुआ लकड़ी का बुद्ध-मुख।",
        "mr": "शांत विश्रांती किंवा चिंतनाच्या जागेसाठी योग्य, हाताने कोरलेले ध्यानमग्न बुद्धमुख.",
    },
    "A terracotta sculpture of Shiva and Parvati, bringing devotional artistry and an earthy finish to your home.": {
        "hi": "शिव और पार्वती की टेराकोटा मूर्ति, घर में भक्तिपूर्ण कला और मिट्टी की सादगी लाती है।",
        "mr": "शिव-पार्वतीची मातीची मूर्ती घरात भक्तिपूर्ण कलाकुसर आणि मातीचा नैसर्गिक साज आणते.",
    },
    "A collection of terracotta deity figurines and diyas for a warm, traditional arrangement during prayer or festivals.": {
        "hi": "पूजा या त्योहारों में पारंपरिक सजावट के लिए टेराकोटा देव-मूर्तियों और दीयों का संग्रह।",
        "mr": "पूजा किंवा सणांच्या वेळी पारंपरिक मांडणीसाठी मातीच्या देवमूर्ती आणि दिव्यांचा संच.",
    },
    "A wall décor arrangement combining a brass lamp and bell, inspired by traditional details of a prayer space.": {
        "hi": "पीतल के दीपक और घंटी वाली दीवार सजावट, पारंपरिक पूजा-स्थल की बारीकियों से प्रेरित।",
        "mr": "पितळी दिवा आणि घंटीची ही भिंतीवरील सजावट पारंपरिक पूजास्थानातील तपशीलांपासून प्रेरित आहे.",
    },
    "Five resin coasters with agate-inspired color and deity motifs, blending everyday function with devotional décor.": {
        "hi": "अकीक जैसे रंगों और देव-आकृतियों वाले पाँच रेज़िन कोस्टर, उपयोगिता और भक्ति-सजावट का मेल।",
        "mr": "अगेटसारख्या रंगछटा आणि देवप्रतिमांची नक्षी असलेले पाच रेझिन कोस्टर उपयोगिता आणि भक्तिसजावट यांचा मेळ घालतात.",
    },
    "A Shiva Lingam-inspired incense burner designed to create a calm focal point in a meditation or prayer area.": {
        "hi": "शिवलिंग से प्रेरित धूपदान, ध्यान या पूजा-स्थल में शांत वातावरण का केंद्र बनाने के लिए।",
        "mr": "शिवलिंगापासून प्रेरित धूपपात्र ध्यानाच्या किंवा पूजेच्या जागेत शांत वातावरण निर्माण करते.",
    },
    "A backflow incense burner featuring Lord Shiva, combining devotional styling with a soothing incense ritual.": {
        "hi": "भगवान शिव की आकृति वाला बैकफ्लो धूपदान, भक्ति-सज्जा और सुकून भरे धूप-अनुष्ठान का मेल।",
        "mr": "भगवान शिवाच्या प्रतिमेचे बॅकफ्लो धूपपात्र भक्तिपूर्ण सजावट आणि शांत धूपविधी यांचा संगम आहे.",
    },
    "A decorative wall plate centered on a goddess face, created as a striking spiritual accent for the home.": {
        "hi": "देवी के मुख वाली सजावटी दीवार-प्लेट, घर के लिए आकर्षक आध्यात्मिक सजावट।",
        "mr": "देवीच्या मुखाची नक्षी असलेली सजावटी भिंतीवरील प्लेट घरासाठी उठावदार आध्यात्मिक सजावट आहे.",
    },
    "A traditional 'Shubh Labh' hanging set to welcome auspicious wishes at an entrance or festive display.": {
        "hi": "प्रवेश-द्वार या उत्सवी सजावट में शुभकामनाओं के स्वागत के लिए पारंपरिक 'शुभ लाभ' तोरण-सेट।",
        "mr": "प्रवेशद्वार किंवा सणाच्या सजावटीत शुभेच्छांचे स्वागत करणारा पारंपरिक 'शुभ लाभ' तोरण-संच.",
    },
    "A winnowing basket decorated with hand-painted deity imagery, bringing folk craft to a devotional display.": {
        "hi": "देव-आकृतियों से हाथ से रंगी सूप की टोकरी, भक्ति-सजावट में लोकशिल्प का स्पर्श जोड़ती है।",
        "mr": "देवप्रतिमा हाताने रंगवलेले सुप भक्तिपूर्ण मांडणीत लोककलेचा साज आणते.",
    },
    "Tribal Beaded Necklace Set": {
        "hi": "जनजातीय मनकों वाला हार-सेट",
        "mr": "आदिवासी मण्यांचा हार-संच",
    },
    "Lotus Beaded Drop Earrings": {
        "hi": "कमल और मनकों वाले लटकन झुमके",
        "mr": "कमळाच्या नक्षीचे मणीदार झुलते कानातले",
    },
    "Fabric Rose Necklace Set": {
        "hi": "कपड़े के गुलाबों वाला हार-सेट",
        "mr": "कापडी गुलाबांचा हार-संच",
    },
    "Bohemian Cowrie Shell Necklace Set": {
        "hi": "बोहेमियन कौड़ी-शंख हार-सेट",
        "mr": "बोहेमियन कवडी-शिंपल्यांचा हार-संच",
    },
    "Golden Spiral Coin Choker Necklace": {
        "hi": "सुनहरी घुमावदार सिक्कों वाला चोकर हार",
        "mr": "सोनेरी वळणदार नाण्यांचा चोकर हार",
    },
    "Handmade Pearl Necklace": {
        "hi": "हस्तनिर्मित मोतियों का हार",
        "mr": "हस्तनिर्मित मोत्यांचा हार",
    },
    "Kundan Bridal Earrings": {
        "hi": "कुंदन दुल्हन झुमके",
        "mr": "कुंदन वधूची कर्णभूषणे",
    },
    "Rajasthani Lac Bangles": {
        "hi": "राजस्थानी लाख की चूड़ियाँ",
        "mr": "राजस्थानी लाखेच्या बांगड्या",
    },
    "Peacock Design Oxidised Necklace": {
        "hi": "मोर डिज़ाइन का ऑक्सिडाइज़्ड हार",
        "mr": "मोराच्या नक्षीचा ऑक्सिडाइझ्ड हार",
    },
    "Hand-painted Wooden Jhumkas": {
        "hi": "हाथ से रंगे लकड़ी के झुमके",
        "mr": "हाताने रंगवलेले लाकडी झुमके",
    },
    "Filigree Silver Pendant": {
        "hi": "फिलिग्री चाँदी का पेंडेंट",
        "mr": "फिलिग्री नक्षीचा चांदीचा पेंडंट",
    },
    "Terracotta Necklace with Bell Charms": {
        "hi": "घंटी वाली सजावट का टेराकोटा हार",
        "mr": "घुंगरांच्या लटकनांचा मातीचा हार",
    },
    "Enamel Work Bangle Set": {
        "hi": "मीनाकारी चूड़ियों का सेट",
        "mr": "मीनाकारी बांगड्यांचा संच",
    },
    "Golden Elephant Head Necklace": {
        "hi": "सुनहरे हाथी-मुख वाला हार",
        "mr": "सोनेरी हत्तीमुखाचा हार",
    },
    "Mirror Work Stud Earrings": {
        "hi": "शीशे की कारीगरी वाले स्टड झुमके",
        "mr": "आरशाच्या नक्षीचे स्टड कानातले",
    },
    "Temple Jewellery Necklace": {
        "hi": "मंदिर-शैली का आभूषण हार",
        "mr": "मंदिर-शैलीचा दागिन्यांचा हार",
    },
    "Oxidised Nose Pin Set": {
        "hi": "ऑक्सिडाइज़्ड नोज़-पिन सेट",
        "mr": "ऑक्सिडाइझ्ड नथांचा संच",
    },
    "Brass Tribal Earrings": {
        "hi": "जनजातीय पीतल के झुमके",
        "mr": "आदिवासी शैलीतील पितळी कर्णभूषणे",
    },
    "Crystal Drop Pendant": {
        "hi": "क्रिस्टल लटकन पेंडेंट",
        "mr": "क्रिस्टलचा झुलता पेंडंट",
    },
    "Antique Silver Kada": {
        "hi": "पुराने अंदाज़ का चाँदी का कड़ा",
        "mr": "पुरातन शैलीतील चांदीचे कडे",
    },
    "Handwoven Thread Necklace": {
        "hi": "हाथ से बुना धागों का हार",
        "mr": "हाताने विणलेल्या धाग्यांचा हार",
    },
    "Polki Bridal Set": {
        "hi": "पोल्की दुल्हन आभूषण सेट",
        "mr": "पोल्की वधू दागिन्यांचा संच",
    },
    "Handcrafted Wooden Earrings": {
        "hi": "हस्तनिर्मित लकड़ी के झुमके",
        "mr": "हस्तनिर्मित लाकडी कानातले",
    },
    "Mirror Beaded Bangles": {
        "hi": "शीशे और मनकों वाली चूड़ियाँ",
        "mr": "आरसा-मण्यांच्या बांगड्या",
    },
    "Pearl Studded Hair Pin": {
        "hi": "मोती जड़ी हेयर पिन",
        "mr": "मोती जडवलेली हेअरपिन",
    },
    "Stone Engraved Toe Rings": {
        "hi": "नक्काशीदार पत्थर के बिछुए",
        "mr": "कोरीव खड्यांची जोडवी",
    },
    "Kundan Bridal Maang Tikka": {
        "hi": "कुंदन दुल्हन मांग टीका",
        "mr": "कुंदन वधूचा मांगटिळा",
    },
    "Handcrafted Wooden & Fabric Trays (Set of 5)": {
        "hi": "हस्तनिर्मित लकड़ी और कपड़े की ट्रे (5 का सेट)",
        "mr": "हस्तनिर्मित लाकडी व कापडी ट्रे (५ चा संच)",
    },
    "Miniature Musical Instrument Set - Type 2": {
        "hi": "छोटे वाद्ययंत्रों का सेट - प्रकार 2",
        "mr": "छोट्या वाद्यांचा संच - प्रकार २",
    },
    "Miniature Musical Instrument Set - Type 1": {
        "hi": "छोटे वाद्ययंत्रों का सेट - प्रकार 1",
        "mr": "छोट्या वाद्यांचा संच - प्रकार १",
    },
    "Hand-painted Marathi Rukhwat Plate": {
        "hi": "हाथ से रंगी मराठी रुखवत थाली",
        "mr": "हाताने रंगवलेली मराठी रुखवत थाळी",
    },
    "Hand-Painted Wedding Thali": {
        "hi": "हाथ से रंगी विवाह थाली",
        "mr": "हाताने रंगवलेली लग्नाची थाळी",
    },
    "Decorative Popsicle Stick House": {
        "hi": "आइसक्रीम स्टिक से बना सजावटी घर",
        "mr": "आईस्क्रीमच्या काड्यांपासून बनवलेले सजावटी घर",
    },
    "Bridal & Groom Decorative Cones": {
        "hi": "दूल्हा-दुल्हन के सजावटी शंकु",
        "mr": "वधू-वरांचे सजावटी शंकू",
    },
    "Miniature Silk Gift Bags (Set of 4)": {
        "hi": "रेशमी छोटे उपहार बैग (4 का सेट)",
        "mr": "रेशमी छोट्या भेटपिशव्या (४ चा संच)",
    },
    "Miniature Paper Dolls in Traditional Attire": {
        "hi": "पारंपरिक वेशभूषा वाली छोटी कागज़ की गुड़िया",
        "mr": "पारंपरिक वेशभूषेतील छोट्या कागदी बाहुल्या",
    },
    "Miniature Wedding Ceremony Thali": {
        "hi": "छोटी विवाह-समारोह थाली",
        "mr": "छोटेखानी लग्नसमारंभाची थाळी",
    },
    "Decorative Winnowing Basket with Wheat": {
        "hi": "गेहूँ वाली सजावटी सूप की टोकरी",
        "mr": "गव्हाचे सजावटी सुप",
    },
    "Large Decorative Rukhwat Basket": {
        "hi": "बड़ी सजावटी रुखवत टोकरी",
        "mr": "मोठी सजावटी रुखवत टोपली",
    },
    "Miniature Tulsi Vivah Set": {
        "hi": "छोटा तुलसी विवाह सेट",
        "mr": "छोटा तुळशीविवाह संच",
    },
    "Terracotta Wind Chimes": {
        "hi": "टेराकोटा विंड चाइम",
        "mr": "मातीचे विंड चाइम",
    },
    "Terracotta Planter with Designs": {
        "hi": "नक्काशी वाला टेराकोटा गमला",
        "mr": "नक्षीची मातीची कुंडी",
    },
    "Decorative Glass Bottle": {
        "hi": "सजावटी काँच की बोतल",
        "mr": "सजावटी काचेची बाटली",
    },
    "Ceramic Utensil Holder": {
        "hi": "सिरेमिक बर्तन होल्डर",
        "mr": "सिरॅमिक भांडी ठेवण्याचे पात्र",
    },
    "Hand-Painted Storage Pot": {
        "hi": "हाथ से रंगा भंडारण पात्र",
        "mr": "हाताने रंगवलेले साठवणीचे भांडे",
    },
    "Elephant-Themed Ceramic Vase": {
        "hi": "हाथी की आकृति वाला सिरेमिक फूलदान",
        "mr": "हत्तीच्या नक्षीची सिरॅमिक फुलदाणी",
    },
    "Small Decorative Jar": {
        "hi": "छोटा सजावटी जार",
        "mr": "छोटी सजावटी बरणी",
    },
    "Terracotta Decorative Lantern": {
        "hi": "टेराकोटा का सजावटी लालटेन",
        "mr": "मातीचा सजावटी कंदील",
    },
    "Black & White Painted Vase": {
        "hi": "काले-सफेद रंग से रंगा फूलदान",
        "mr": "काळ्या-पांढऱ्या रंगात रंगवलेली फुलदाणी",
    },
    "Red Decorative Stacked Pots": {
        "hi": "लाल सजावटी परतदार गमले",
        "mr": "लाल सजावटी एकावर-एक कुंड्या",
    },
    "Traditional Clay Jug with Carvings": {
        "hi": "नक्काशी वाला पारंपरिक मिट्टी का घड़ा",
        "mr": "कोरीव नक्षीचा पारंपरिक मातीचा घडा",
    },
    "Decorative Leaf Wall Hanging": {
        "hi": "पत्ते की सजावटी दीवार-लटकन",
        "mr": "पानाची सजावटी भिंतीवरील लटकन",
    },
    "Set of 4 Wooden Bowls": {
        "hi": "लकड़ी के कटोरों का सेट (4 का सेट)",
        "mr": "लाकडी बाऊलचा संच (४ नग)",
    },
    "Decorative Plates (Set of 4)": {
        "hi": "सजावटी प्लेटें (4 का सेट)",
        "mr": "सजावटी प्लेट्स (४ चा संच)",
    },
    "Blue Elephant Painted Vase": {
        "hi": "नीले हाथी की चित्रकारी वाला फूलदान",
        "mr": "निळ्या हत्तीचे चित्र असलेली फुलदाणी",
    },
    "Terracotta Diya Lamp": {
        "hi": "टेराकोटा का दीया",
        "mr": "मातीचा दिवा",
    },
    "Terracotta Wind Chime Bell": {
        "hi": "टेराकोटा की विंड चाइम घंटी",
        "mr": "मातीची विंड चाइम घंटी",
    },
    "Set of 2 Camel Planters": {
        "hi": "ऊँट के आकार के गमले (2 का सेट)",
        "mr": "उंटाच्या आकाराच्या कुंड्या (२ चा संच)",
    },
    "Abstract Ceramic Flower Vase": {
        "hi": "अमूर्त डिज़ाइन का सिरेमिक फूलदान",
        "mr": "अमूर्त रचनेची सिरॅमिक फुलदाणी",
    },
    "Set of 3 Humanoid Figurines": {
        "hi": "मानवाकार मूर्तियाँ (3 का सेट)",
        "mr": "मानवाकृती मूर्ती (३ चा संच)",
    },
    "Hand-painted Figurine Planters (Set of 2)": {
        "hi": "हाथ से रंगे मूर्ति-आकार के गमले (2 का सेट)",
        "mr": "हाताने रंगवलेल्या मूर्तीरूप कुंड्या (२ चा संच)",
    },
    "Large Elephant Terracotta Planter": {
        "hi": "हाथी की आकृति वाला बड़ा टेराकोटा गमला",
        "mr": "हत्तीच्या आकाराची मोठी मातीची कुंडी",
    },
    "Handmade Ceramic Tic-Tac-Toe Set": {
        "hi": "हस्तनिर्मित सिरेमिक टिक-टैक-टो सेट",
        "mr": "हस्तनिर्मित सिरॅमिक टिक-टॅक-टो संच",
    },
    "Ceramic Sloth Incense Holder": {
        "hi": "स्लॉथ डिज़ाइन वाला सिरेमिक धूपदान",
        "mr": "स्लॉथच्या आकाराचे सिरॅमिक धूपपात्र",
    },
    "Miniature Terracotta Kitchen Set": {
        "hi": "छोटा टेराकोटा रसोई सेट",
        "mr": "छोटेखानी मातीच्या भांड्यांचा संच",
    },
    "Mushroom Brush Holder": {
        "hi": "मशरूम आकार का ब्रश होल्डर",
        "mr": "मशरूमच्या आकाराचे ब्रश ठेवण्याचे पात्र",
    },
    "Handmade Earthenware Money Bank": {
        "hi": "हस्तनिर्मित मिट्टी की गुल्लक",
        "mr": "हाताने बनवलेली मातीची बचतपेटी",
    },
    "Hanging Terracotta Planters (Set of 4)": {
        "hi": "लटकते टेराकोटा गमले (4 का सेट)",
        "mr": "टांगत्या मातीच्या कुंड्या (४ चा संच)",
    },
    "Set of Miniature Divine Figurines": {
        "hi": "छोटी दिव्य मूर्तियों का सेट",
        "mr": "छोट्या दिव्य मूर्तींचा संच",
    },
    "Lakshmi-Ganesha Tea Light Holder": {
        "hi": "लक्ष्मी-गणेश टी-लाइट होल्डर",
        "mr": "लक्ष्मी-गणेश टी-लाइट धारक",
    },
    "Terracotta Divine Lamp Stand": {
        "hi": "टेराकोटा का दिव्य दीप-स्टैंड",
        "mr": "मातीचा दिव्य दिवा-स्टँड",
    },
    "Handcrafted Coconut Shell Incense Burner": {
        "hi": "हस्तनिर्मित नारियल-खोल धूपदान",
        "mr": "हस्तनिर्मित नारळाच्या करवंटीचे धूपपात्र",
    },
    "Miniature Stone Temple Replica": {
        "hi": "पत्थर के मंदिर की छोटी प्रतिकृति",
        "mr": "दगडी मंदिराची छोटी प्रतिकृती",
    },
    "Mirror Mosaic Elephant Wall Decor": {
        "hi": "शीशे की मोज़ेक वाला हाथी दीवार-अलंकरण",
        "mr": "आरशाच्या मोझॅकचे हत्तीच्या आकारातील भिंतीवरील सजावट",
    },
    "Hand-knitted Lotus Dress for Krishna Figurine": {
        "hi": "कृष्ण मूर्ति के लिए हाथ से बुनी कमल पोशाक",
        "mr": "कृष्णमूर्तीसाठी हाताने विणलेला कमळाचा पोशाख",
    },
    "Hand-knitted White & Red Floral Garland": {
        "hi": "हाथ से बुनी सफेद-लाल फूलों की माला",
        "mr": "हाताने विणलेली पांढरी-लाल फुलांची माळ",
    },
    "Servdharam Ganga Jal (250ml)": {
        "hi": "सर्वधर्म गंगाजल (250 मिली)",
        "mr": "सर्वधर्म गंगाजल (२५० मिली)",
    },
    "Complete Karwa Chauth Puja Kit": {
        "hi": "करवा चौथ की संपूर्ण पूजा सामग्री",
        "mr": "करवा चौथची संपूर्ण पूजासामग्री",
    },
    "Hand-carved Wooden Buddha Head": {
        "hi": "हाथ से तराशा लकड़ी का बुद्ध-मुख",
        "mr": "हाताने कोरलेले लाकडी बुद्धमुख",
    },
    "Terracotta Sculpture of Shiva Parvati": {
        "hi": "शिव-पार्वती की टेराकोटा मूर्ति",
        "mr": "शिव-पार्वतीची मातीची मूर्ती",
    },
    "Terracotta Deity Figurines & Diyas": {
        "hi": "टेराकोटा देव-मूर्तियाँ और दीये",
        "mr": "मातीच्या देवमूर्ती आणि दिवे",
    },
    "Brass Lamp & Bell Wall Decor": {
        "hi": "पीतल के दीपक और घंटी की दीवार सजावट",
        "mr": "पितळी दिवा आणि घंटीची भिंतीवरील सजावट",
    },
    "Resin Agate Deity Coasters (Set of 5)": {
        "hi": "अकीक डिज़ाइन वाले देव-आकृति रेज़िन कोस्टर (5 का सेट)",
        "mr": "अगेट नक्षीचे देवप्रतिमांचे रेझिन कोस्टर (५ चा संच)",
    },
    "Shiva Lingam Waterfall Incense Burner": {
        "hi": "शिवलिंग झरना धूपदान",
        "mr": "शिवलिंग धबधबा धूपपात्र",
    },
    "Lord Shiva Backflow Incense Burner": {
        "hi": "भगवान शिव बैकफ्लो धूपदान",
        "mr": "भगवान शिव बॅकफ्लो धूपपात्र",
    },
    "Goddess Face Wall Plate": {
        "hi": "देवी-मुख वाली दीवार प्लेट",
        "mr": "देवीच्या मुखाची भिंतीवरील प्लेट",
    },
    "'Shubh Labh' Wall Hanging Set": {
        "hi": "'शुभ लाभ' दीवार-लटकन सेट",
        "mr": "'शुभ लाभ' भिंतीवरील लटकन संच",
    },
    "Hand-painted Deity Winnowing Basket": {
        "hi": "हाथ से रंगी देव-आकृति वाली सूप की टोकरी",
        "mr": "देवप्रतिमा हाताने रंगवलेले सुप",
    },
    "Pillar Candle with Glitter & Jewels": {
        "hi": "चमक और रत्नों वाली स्तंभाकार मोमबत्ती",
        "mr": "ग्लिटर आणि खड्यांनी सजवलेली खांबाच्या आकाराची मेणबत्ती",
    },
    "A decorative pillar candle embellished with gold glitter and small jewels, perfect for festive occasions.": {
        "hi": "सोनेरी चमक और छोटे रत्नों से सजी सजावटी स्तंभाकार मोमबत्ती, उत्सवों के लिए सुंदर।",
        "mr": "सोनेरी ग्लिटर आणि छोट्या खड्यांनी सजवलेली ही खांबाच्या आकाराची मेणबत्ती सणांसाठी सुंदर आहे.",
    },
    "Assorted Scented Jar Candles (Set of 4)": {
        "hi": "खुशबूदार जार मोमबत्तियाँ (4 का सेट)",
        "mr": "सुगंधी जार मेणबत्त्या (४ चा संच)",
    },
    "A collection of four scented candles in glass jars, each with a different aroma to create a unique mood.": {
        "hi": "काँच के जार में चार सुगंधित मोमबत्तियाँ, हर खुशबू घर में अलग माहौल बनाती है।",
        "mr": "काचेच्या जारमधील चार सुगंधी मेणबत्त्या; प्रत्येक सुगंध घरात वेगळे वातावरण निर्माण करतो.",
    },
    "Wooden Base with Scented Candles": {
        "hi": "सुगंधित मोमबत्तियों वाला लकड़ी का आधार",
        "mr": "सुगंधी मेणबत्त्यांसह लाकडी आधार",
    },
    "A trio of scented jar candles artfully arranged on a rustic wooden base, tied with a jute rope for a natural look.": {
        "hi": "देहाती लकड़ी के आधार पर सजी तीन सुगंधित जार मोमबत्तियाँ, प्राकृतिक रूप के लिए जूट की रस्सी से बँधी।",
        "mr": "नैसर्गिक लुकसाठी ज्यूटच्या दोरीने बांधलेल्या, जुन्या ढंगाच्या लाकडी आधारावर सजवलेल्या तीन सुगंधी जार मेणबत्त्या.",
    },
    "Hand-painted Terracotta Diyas (Set of 6)": {
        "hi": "हाथ से रंगे टेराकोटा दीये (6 का सेट)",
        "mr": "हाताने रंगवलेले मातीचे दिवे (६ चा संच)",
    },
    "A set of six traditional terracotta diyas (oil lamps) with intricate hand-painted designs, perfect for festivals and puja.": {
        "hi": "बारीक हाथ की चित्रकारी वाले छह पारंपरिक टेराकोटा दीये, पूजा और त्योहारों के लिए उपयुक्त।",
        "mr": "नाजूक हस्तचित्रकलेचे सहा पारंपरिक मातीचे दिवे, पूजा आणि सणांसाठी योग्य.",
    },
    "Custom Resin Letter/Alphabet": {
        "hi": "कस्टम रेज़िन अक्षर",
        "mr": "कस्टम रेझिन अक्षर",
    },
    "A resin art piece shaped like a letter of the alphabet, with intricate fillings of glitter and dried flowers.": {
        "hi": "अक्षर के आकार की रेज़िन कलाकृति, जिसमें चमक और सूखे फूलों की बारीक सजावट है।",
        "mr": "अक्षराच्या आकारातील रेझिन कलाकृती, ग्लिटर आणि सुकवलेल्या फुलांच्या नाजूक सजावटीसह.",
    },
    "Hand-poured Bubble Candles (Set of 4)": {
        "hi": "हाथ से ढाली गई बबल मोमबत्तियाँ (4 का सेट)",
        "mr": "हाताने ओतून बनवलेल्या बबल मेणबत्त्या (४ चा संच)",
    },
    "A set of four small, cube-shaped bubble candles in pastel colors, perfect for modern home decor.": {
        "hi": "हल्के पेस्टल रंगों की चार छोटी घनाकार बबल मोमबत्तियाँ, आधुनिक घर की सजावट के लिए।",
        "mr": "पेस्टल रंगांच्या चार छोट्या घनाकार बबल मेणबत्त्या आधुनिक घराच्या सजावटीसाठी सुंदर आहेत.",
    },
    "Geode-Inspired Resin Wall Clock": {
        "hi": "जियोड डिज़ाइन वाली रेज़िन दीवार घड़ी",
        "mr": "जिओड-प्रेरित रेझिन भिंतीवरील घड्याळ",
    },
    "A circular wall clock with a geode-inspired resin design, featuring gold flakes and shades of blue and white.": {
        "hi": "जियोड से प्रेरित रेज़िन डिज़ाइन वाली गोल दीवार घड़ी, जिसमें सुनहरी पत्तियाँ और नीले-सफेद रंग हैं।",
        "mr": "जिओडपासून प्रेरित रेझिन नक्षीचे गोल भिंतीवरील घड्याळ; त्यावर सोनेरी कण आणि निळ्या-पांढऱ्या छटा आहेत.",
    },
    "Resin & Agate Tray": {
        "hi": "रेज़िन और अकीक की ट्रे",
        "mr": "रेझिन आणि अगेटची ट्रे",
    },
    "A decorative serving tray made from resin with a marbled pattern, adorned with a slice of natural agate stone.": {
        "hi": "संगमरमर जैसी नक्काशी वाली रेज़िन की सजावटी ट्रे, जिस पर प्राकृतिक अकीक पत्थर का टुकड़ा जड़ा है।",
        "mr": "संगमरवरी नक्षीच्या रेझिनच्या सजावटी ट्रेवर नैसर्गिक अगेट दगडाचा तुकडा जडवलेला आहे.",
    },
    "Terracotta Diffuser & Tea Light Holder": {
        "hi": "टेराकोटा डिफ्यूज़र और टी-लाइट होल्डर",
        "mr": "मातीचा सुगंध-विसारक आणि टी-लाइट धारक",
    },
    "A two-piece terracotta set, including a base for a tea light and a top for essential oils or wax melts.": {
        "hi": "दो टुकड़ों का टेराकोटा सेट: नीचे टी-लाइट रखने का आधार और ऊपर एसेंशियल ऑयल या वैक्स मेल्ट रखने की जगह।",
        "mr": "दोन भागांचा मातीचा संच: खाली टी-लाइट ठेवण्याचा आधार आणि वर सुगंधी तेल किंवा वितळणारे मेण ठेवण्याची जागा.",
    },
    "Shell-Shaped Wax Candles": {
        "hi": "सीप के आकार की मोमबत्तियाँ",
        "mr": "शिंपल्याच्या आकारातील मेणबत्त्या",
    },
    "A set of unique, shell-shaped wax candles in various colors, adding a coastal feel to your decor.": {
        "hi": "अलग-अलग रंगों की अनोखी सीप-आकार की मोमबत्तियाँ, सजावट में समुद्र-तट जैसा एहसास जोड़ती हैं।",
        "mr": "विविध रंगांच्या शिंपल्याच्या आकारातील या अनोख्या मेणबत्त्या सजावटीला समुद्रकिनाऱ्याचा भास देतात.",
    },
    "Handmade Ceramic Candle Holder": {
        "hi": "हस्तनिर्मित सिरेमिक मोमबत्ती-स्टैंड",
        "mr": "हाताने बनवलेले सिरॅमिक मेणबत्तीदान",
    },
    "A rustic, handmade ceramic candle holder with a textured surface and a slot for a small taper candle.": {
        "hi": "खुरदरी बनावट वाला हस्तनिर्मित सिरेमिक मोमबत्ती-स्टैंड, जिसमें पतली छोटी मोमबत्ती रखने की जगह है।",
        "mr": "खडबडीत पोताचे हाताने बनवलेले सिरॅमिक मेणबत्तीदान; त्यात छोटी निमुळती मेणबत्ती ठेवता येते.",
    },
    "Resin Art Wall Hanging": {
        "hi": "रेज़िन कला की दीवार सजावट",
        "mr": "रेझिन कलाकृतीची भिंतीवरील सजावट",
    },
    "A circular resin art wall decor piece featuring a vibrant mix of colors and a shimmering finish.": {
        "hi": "चमकदार फिनिश और चटख रंगों के मेल वाली गोल रेज़िन कलाकृति, दीवार सजाने के लिए।",
        "mr": "चमकदार फिनिश आणि उठावदार रंगसंगतीची गोल रेझिन कलाकृती भिंतीच्या सजावटीसाठी.",
    },
    "Assorted Pillar Candles (Set of 3)": {
        "hi": "अलग-अलग स्तंभाकार मोमबत्तियाँ (3 का सेट)",
        "mr": "विविध आकारांच्या खांबाच्या मेणबत्त्या (३ चा संच)",
    },
    "A set of three cylindrical pillar candles in different sizes and colors, perfect for a layered centerpiece.": {
        "hi": "अलग-अलग आकार और रंगों की तीन बेलनाकार मोमबत्तियाँ, सजावटी केंद्रबिंदु बनाने के लिए।",
        "mr": "वेगवेगळ्या आकारांच्या आणि रंगांच्या तीन दंडगोलाकार मेणबत्त्या टेबलाच्या मध्यभागी सजवण्यासाठी योग्य.",
    },
    "Hand-Painted Resin Name Plate": {
        "hi": "हाथ से रंगी रेज़िन नेमप्लेट",
        "mr": "हाताने रंगवलेली रेझिन नामफलक",
    },
    "A custom-made resin art nameplate, personalized with names and decorated with metallic and floral accents.": {
        "hi": "नाम के अनुसार बनाई गई रेज़िन नेमप्लेट, धातुई और फूलों की सजावट से सजी।",
        "mr": "नावानुसार तयार केलेला रेझिन नामफलक धातूच्या आणि फुलांच्या सजावटीने नटवलेला आहे.",
    },
    "Decorative Resin Ganesha Idol": {
        "hi": "सजावटी रेज़िन गणेश मूर्ति",
        "mr": "सजावटी रेझिन गणेशमूर्ती",
    },
    "A seated resin sculpture of Lord Ganesha, with a matte finish and decorated with colorful hand-painted details.": {
        "hi": "बैठी मुद्रा में भगवान गणेश की रेज़िन मूर्ति, मैट फिनिश और रंगीन हाथ की चित्रकारी से सजी।",
        "mr": "बैठलेल्या मुद्रेतील भगवान गणेशाची रेझिन मूर्ती मॅट फिनिश आणि रंगीत हस्तचित्रांनी सजवलेली आहे.",
    },
    "Resin & Clay Coasters (Set of 4)": {
        "hi": "रेज़िन और मिट्टी के कोस्टर (4 का सेट)",
        "mr": "रेझिन आणि मातीचे कोस्टर (४ चा संच)",
    },
    "A set of four coasters with a unique design featuring a combination of resin and intricate claywork in a circular pattern.": {
        "hi": "गोलाकार डिज़ाइन में रेज़िन और बारीक मिट्टी की कारीगरी से बने चार अनोखे कोस्टर।",
        "mr": "गोलाकार नक्षीत रेझिन आणि मातीच्या नाजूक कलाकुसरीचा संगम असलेले चार अनोखे कोस्टर.",
    },
    "Hand-painted Terracotta Tea Light Holders": {
        "hi": "हाथ से रंगे टेराकोटा टी-लाइट होल्डर",
        "mr": "हाताने रंगवलेले मातीचे टी-लाइट धारक",
    },
    "A set of traditional terracotta tea light holders, painted in a striking black and white geometric pattern.": {
        "hi": "काले-सफेद ज्यामितीय पैटर्न में रंगे पारंपरिक टेराकोटा टी-लाइट होल्डरों का सेट।",
        "mr": "ठळक काळ्या-पांढऱ्या भौमितिक नक्षीने रंगवलेल्या पारंपरिक मातीच्या टी-लाइट धारकांचा संच.",
    },
    "Floral Resin & Wood Name Plate": {
        "hi": "फूलों वाली रेज़िन और लकड़ी की नेमप्लेट",
        "mr": "फुलांच्या नक्षीचा रेझिन आणि लाकडी नामफलक",
    },
    "A custom resin and wood nameplate with a floral motif, featuring names written in elegant script.": {
        "hi": "फूलों की आकृति वाली कस्टम रेज़िन और लकड़ी की नेमप्लेट, जिस पर नाम सुंदर लिखावट में हैं।",
        "mr": "फुलांच्या नक्षीचा कस्टम रेझिन-लाकडी नामफलक, ज्यावर नावे सुंदर अक्षरांत लिहिली आहेत.",
    },
    "Resin Art Wall Decor Frame": {
        "hi": "रेज़िन कला का दीवार सजावट फ्रेम",
        "mr": "रेझिन कलाकृतीची भिंतीवरील सजावटीची चौकट",
    },
    "A decorative wall art frame made from a blend of resin and metallic pigments, with a shimmering, marbled finish.": {
        "hi": "रेज़िन और धातुई रंगद्रव्यों से बना सजावटी फ्रेम, चमकदार संगमरमर जैसी फिनिश के साथ।",
        "mr": "रेझिन आणि धातूच्या रंगद्रव्यांपासून बनवलेली सजावटी चौकट; चमकदार संगमरवरी पोतासह.",
    },
    "Textured Ceramic Vase": {
        "hi": "बनावटदार सिरेमिक फूलदान",
        "mr": "पोतदार सिरॅमिक फुलदाणी",
    },
    "A small, textured ceramic vase with a matte finish, ideal for a single stem or a small bouquet.": {
        "hi": "मैट फिनिश वाला छोटा बनावटदार सिरेमिक फूलदान, एक फूल या छोटे गुलदस्ते के लिए उपयुक्त।",
        "mr": "मॅट फिनिशची छोटी पोतदार सिरॅमिक फुलदाणी, एक फूल किंवा छोट्या पुष्पगुच्छासाठी योग्य.",
    },
    "Hand-painted Ceramic Serving Dish": {
        "hi": "हाथ से रंगी सिरेमिक परोसने की थाली",
        "mr": "हाताने रंगवलेली सिरॅमिक वाढण्याची थाळी",
    },
    "A square-shaped ceramic serving dish with a unique hand-painted design in shades of blue and gold.": {
        "hi": "नीले और सुनहरे रंगों की अनोखी हाथ की चित्रकारी वाली चौकोर सिरेमिक परोसने की थाली।",
        "mr": "निळ्या आणि सोनेरी छटांतील अनोख्या हस्तचित्राची चौकोनी सिरॅमिक वाढण्याची थाळी.",
    },
    "Decorative Miniature Clay Pots": {
        "hi": "सजावटी छोटी मिट्टी की मटकियाँ",
        "mr": "सजावटी छोट्या मातीच्या कुंड्या",
    },
    "A set of small, decorative clay pots with subtle, hand-painted designs, suitable for small plants or as standalone decor.": {
        "hi": "हल्की हाथ की चित्रकारी वाली छोटी सजावटी मिट्टी की मटकियाँ, नन्हे पौधों या अलग से सजाने के लिए।",
        "mr": "नाजूक हस्तचित्रांची छोटी सजावटी मातीची भांडी, लहान रोपे लावण्यासाठी किंवा स्वतंत्र सजावटीसाठी.",
    },
    "Carved Wooden Elephant": {
        "hi": "नक्काशीदार लकड़ी का हाथी",
        "mr": "कोरीव लाकडी हत्ती",
    },
    "A small, intricately carved wooden figurine of an elephant, a traditional symbol of good luck.": {
        "hi": "बारीकी से तराशी गई हाथी की छोटी लकड़ी की मूर्ति, जिसे पारंपरिक रूप से शुभता का प्रतीक माना जाता है।",
        "mr": "बारीक कोरीव कामाची हत्तीची छोटी लाकडी मूर्ती; पारंपरिकरीत्या शुभतेचे प्रतीक मानली जाते.",
    },
    "Colorful Hand-painted Kettle": {
        "hi": "रंगीन हाथ से रंगी केतली",
        "mr": "रंगीत हाताने रंगवलेली केतली",
    },
    "A decorative metal kettle with vibrant, hand-painted floral patterns, perfect as a centerpiece or home accent.": {
        "hi": "चटख फूलों की हाथ की चित्रकारी वाली धातु की सजावटी केतली, मेज़ के केंद्र या घर की सजावट के लिए।",
        "mr": "उठावदार फुलांच्या हस्तचित्रांची धातूची सजावटी केतली, टेबलच्या मध्यभागी किंवा घरसजावटीसाठी सुंदर.",
    },
    "Resin & Pressed Flower Tray": {
        "hi": "रेज़िन और दबे फूलों की ट्रे",
        "mr": "रेझिन आणि दाबलेल्या फुलांची ट्रे",
    },
    "A decorative tray made from resin, with dried pressed flowers and golden flakes embedded inside for a luxurious feel.": {
        "hi": "रेज़िन की सजावटी ट्रे, जिसमें सूखे दबे फूल और सुनहरे कण जड़े हैं, जो इसे खास चमक देते हैं।",
        "mr": "रेझिनच्या सजावटी ट्रेमध्ये वाळवलेली दाबलेली फुले आणि सोनेरी कण जडवले आहेत, ज्यामुळे तिला खास झळाळी मिळते.",
    },
    "Hand-woven Jute Rug": {
        "hi": "हाथ से बुना जूट का गलीचा",
        "mr": "हाताने विणलेली ज्यूटची चटई",
    },
    "A circular hand-woven jute rug with a fringed border, adding a natural and earthy texture to any room.": {
        "hi": "झालरदार किनारे वाला गोल हाथ-बुना जूट गलीचा, किसी भी कमरे में प्राकृतिक और मिट्टी-सा एहसास जोड़ता है।",
        "mr": "झालरदार कडेची गोल हातमागावर विणलेली ज्यूटची चटई कोणत्याही खोलीला नैसर्गिक पोत देते.",
    },
    "Hand-painted Wooden Wall Hanging": {
        "hi": "हाथ से रंगी लकड़ी की दीवार सजावट",
        "mr": "हाताने रंगवलेली लाकडी भिंतीवरील सजावट",
    },
    "A decorative wooden wall hanging with traditional hand-painted patterns and a central mirror.": {
        "hi": "पारंपरिक हाथ की चित्रकारी और बीच में लगे आईने वाली सजावटी लकड़ी की दीवार सजावट।",
        "mr": "पारंपरिक हस्तचित्रांची नक्षी आणि मध्यभागी आरसा असलेली सजावटी लाकडी भिंतीवरील वस्तू.",
    },
    "Set of Hand-painted Vases": {
        "hi": "हाथ से रंगे फूलदानों का सेट",
        "mr": "हाताने रंगवलेल्या फुलदाण्यांचा संच",
    },
    "A collection of assorted vases, each with a unique, hand-painted design in shades of blue and white.": {
        "hi": "नीले-सफेद रंगों में अलग-अलग अनोखी हाथ की चित्रकारी वाले फूलदानों का संग्रह।",
        "mr": "निळ्या-पांढऱ्या छटांतील वेगवेगळ्या हस्तचित्रांची फुलदाण्यांचा संग्रह.",
    },
    "Clay Decorative Plate": {
        "hi": "मिट्टी की सजावटी प्लेट",
        "mr": "मातीची सजावटी प्लेट",
    },
    "A decorative clay plate with a beige and brown patterned finish, suitable as a centerpiece or wall decor.": {
        "hi": "बेज और भूरे पैटर्न वाली मिट्टी की सजावटी प्लेट, मेज़ की शोभा या दीवार सजाने के लिए।",
        "mr": "बेज आणि तपकिरी नक्षीची मातीची सजावटी प्लेट, टेबलच्या मध्यभागी किंवा भिंतीवर लावण्यासाठी.",
    },
    "Hand-Painted Bird Figurines (Set of 3)": {
        "hi": "हाथ से रंगी चिड़ियों की मूर्तियाँ (3 का सेट)",
        "mr": "हाताने रंगवलेल्या पक्ष्यांच्या मूर्ती (३ चा संच)",
    },
    "A set of three small, ceramic or clay bird figurines with intricate hand-painted details.": {
        "hi": "बारीक हाथ की चित्रकारी वाली सिरेमिक या मिट्टी की तीन छोटी चिड़ियों की मूर्तियाँ।",
        "mr": "नाजूक हस्तचित्रांची सिरेमिक किंवा मातीच्या तीन छोट्या पक्ष्यांच्या मूर्ती.",
    },
    "Terracotta Flower Pot with Stand": {
        "hi": "स्टैंड वाला टेराकोटा फूलदान",
        "mr": "स्टँडसह मातीची फुलकुंडी",
    },
    "A classic terracotta flower pot with a simple, dark metal stand, perfect for indoor plants.": {
        "hi": "गहरे रंग के साधारण धातु स्टैंड वाला पारंपरिक टेराकोटा गमला, घर के पौधों के लिए।",
        "mr": "साध्या गडद रंगाच्या धातूच्या स्टँडसह पारंपरिक मातीची फुलकुंडी, घरातील रोपांसाठी योग्य.",
    },
    "Resin-framed Wall Art": {
        "hi": "रेज़िन फ्रेम वाली दीवार कला",
        "mr": "रेझिनच्या चौकटीतील भिंतीवरील कलाकृती",
    },
    "A large wall art piece with a unique abstract design and a textured resin frame.": {
        "hi": "अनोखे अमूर्त डिज़ाइन और बनावटदार रेज़िन फ्रेम वाली बड़ी दीवार कलाकृति।",
        "mr": "अनोखी अमूर्त रचना आणि पोतदार रेझिनची चौकट असलेली मोठी भिंतीवरील कलाकृती.",
    },
    "Miniature Terracotta Lantern": {
        "hi": "छोटा टेराकोटा लालटेन",
        "mr": "छोटा मातीचा कंदील",
    },
    "A small, decorative terracotta lantern with detailed cutouts for light to shine through.": {
        "hi": "रोशनी छनकर आने के लिए बारीक कटाव वाला छोटा सजावटी टेराकोटा लालटेन।",
        "mr": "प्रकाश बाहेर पडण्यासाठी बारीक नक्षीकामाची छिद्रे असलेला छोटा सजावटी मातीचा कंदील.",
    },
    "Decorative Terracotta Wall Plate": {
        "hi": "सजावटी टेराकोटा दीवार प्लेट",
        "mr": "सजावटी मातीची भिंतीवरील प्लेट",
    },
    "A decorative terracotta plate with a white and blue hand-painted design, ideal for hanging on a wall.": {
        "hi": "सफेद-नीले रंग की हाथ की चित्रकारी वाली टेराकोटा प्लेट, दीवार पर सजाने के लिए।",
        "mr": "पांढऱ्या-निळ्या हस्तचित्रांची मातीची प्लेट भिंतीवर लावण्यासाठी योग्य आहे.",
    },
    "Hand-painted Wooden Stool": {
        "hi": "हाथ से रंगा लकड़ी का स्टूल",
        "mr": "हाताने रंगवलेले लाकडी स्टूल",
    },
    "A small, handcrafted wooden stool with a vibrant hand-painted top featuring a mandala-like design.": {
        "hi": "मंडला जैसी रंगीन हाथ की चित्रकारी वाली सतह का छोटा हस्तनिर्मित लकड़ी का स्टूल।",
        "mr": "मंडलासारखी रंगीत हस्तचित्रकला असलेला छोटा हाताने बनवलेला लाकडी स्टूल.",
    },
    "Terracotta Vase with Handles": {
        "hi": "हैंडल वाला टेराकोटा फूलदान",
        "mr": "हाताळ्यांची मातीची फुलदाणी",
    },
    "A unique terracotta vase with handles, featuring a geometric pattern and a natural, rustic finish.": {
        "hi": "ज्यामितीय पैटर्न और प्राकृतिक देहाती फिनिश वाला अनोखा हैंडलदार टेराकोटा फूलदान।",
        "mr": "भौमितिक नक्षी आणि नैसर्गिक, ग्रामीण पोताची हाताळ्यांची अनोखी मातीची फुलदाणी.",
    },
    "Hand-painted Terracotta Jar": {
        "hi": "हाथ से रंगा टेराकोटा जार",
        "mr": "हाताने रंगवलेली मातीची बरणी",
    },
    "A small terracotta jar with a lid, featuring a geometric hand-painted design in white and red.": {
        "hi": "ढक्कन वाला छोटा टेराकोटा जार, जिस पर सफेद और लाल रंग का ज्यामितीय डिज़ाइन हाथ से बनाया गया है।",
        "mr": "पांढऱ्या आणि लाल रंगांची भौमितिक नक्षी हाताने रंगवलेली झाकणाची छोटी मातीची बरणी.",
    },
    "Decorative Macrame Wall Hanging": {
        "hi": "सजावटी मैक्रेमे दीवार सजावट",
        "mr": "सजावटी मॅक्रेमे भिंतीवरील लटकन",
    },
    "A beautiful macrame wall hanging with a detailed woven pattern and tassels, adding a bohemian touch to any room.": {
        "hi": "बारीक बुनी नक्काशी और लटकनों वाली मैक्रेमे दीवार सजावट, कमरे में बोहेमियन अंदाज़ जोड़ती है।",
        "mr": "नाजूक विणकामाच्या नक्षीची आणि लटकनांची मॅक्रेमे भिंतीवरील सजावट खोलीला बोहेमियन लुक देते.",
    },
    "Hand-painted Ceramic Bowl": {
        "hi": "हाथ से रंगा सिरेमिक कटोरा",
        "mr": "हाताने रंगवलेला सिरॅमिक बाऊल",
    },
    "A small, hand-painted ceramic bowl with a unique floral design on the inside.": {
        "hi": "भीतर की सतह पर अनोखी फूलों की चित्रकारी वाला छोटा हाथ से रंगा सिरेमिक कटोरा।",
        "mr": "आतील बाजूस अनोखी फुलांची नक्षी हाताने रंगवलेला छोटा सिरॅमिक बाऊल.",
    },
    "Decorative Glass Bottle with Jute & Flowers": {
        "hi": "जूट और फूलों वाली सजावटी काँच की बोतल",
        "mr": "ज्यूट आणि फुलांनी सजवलेली काचेची बाटली",
    },
    "A decorative glass bottle wrapped in jute string and adorned with small artificial flowers.": {
        "hi": "जूट की डोरी से लिपटी और छोटे कृत्रिम फूलों से सजी सजावटी काँच की बोतल।",
        "mr": "ज्यूटच्या दोरीने गुंडाळलेली आणि छोट्या कृत्रिम फुलांनी सजवलेली काचेची बाटली.",
    },
    "Hand-woven Planter Basket": {
        "hi": "हाथ से बुनी गमला रखने की टोकरी",
        "mr": "हाताने विणलेली कुंडीची टोपली",
    },
    "A rustic, hand-woven basket perfect for holding a plant pot, with a natural and textured look.": {
        "hi": "प्राकृतिक बनावट वाली देहाती हाथ-बुनी टोकरी, गमला रखने के लिए उपयुक्त।",
        "mr": "नैसर्गिक पोताची ग्रामीण ढंगाची हाताने विणलेली टोपली, कुंडी ठेवण्यासाठी योग्य.",
    },
    "Decorative Terracotta Pot with Stand": {
        "hi": "स्टैंड वाला सजावटी टेराकोटा गमला",
        "mr": "स्टँडसह सजावटी मातीची कुंडी",
    },
    "A decorative terracotta pot with intricate carvings, seated on a sturdy wooden stand.": {
        "hi": "बारीक नक्काशी वाला सजावटी टेराकोटा गमला, मजबूत लकड़ी के स्टैंड पर रखा हुआ।",
        "mr": "बारीक कोरीव नक्षीची सजावटी मातीची कुंडी मजबूत लाकडी स्टँडवर ठेवलेली आहे.",
    },
    "Hand-painted Wall Mirror": {
        "hi": "हाथ से रंगा दीवार का आईना",
        "mr": "हाताने रंगवलेला भिंतीवरील आरसा",
    },
    "A circular wall mirror with a beautifully hand-painted border featuring traditional Indian folk art.": {
        "hi": "पारंपरिक भारतीय लोककला की सुंदर हाथ की चित्रकारी वाली किनारी का गोल दीवार आईना।",
        "mr": "पारंपरिक भारतीय लोककलेची सुंदर हस्तचित्रित किनार असलेला गोल भिंतीवरील आरसा.",
    },
    "Set of Miniature Clay Vases": {
        "hi": "छोटे मिट्टी के फूलदान (सेट)",
        "mr": "छोट्या मातीच्या फुलदाण्यांचा संच",
    },
    "Set of Miniature Clay Pots": {
        "hi": "छोटी मिट्टी की मटकियों का सेट",
        "mr": "छोट्या मातीच्या कुंड्यांचा संच",
    },
    "A set of several small, handmade clay vases in different shapes and sizes.": {
        "hi": "अलग-अलग आकार और माप के कई छोटे हस्तनिर्मित मिट्टी के फूलदानों का सेट।",
        "mr": "वेगवेगळ्या आकारांच्या आणि मापांच्या अनेक छोट्या हाताने बनवलेल्या मातीच्या फुलदाण्यांचा संच.",
    },
    "Hand-Painted Clay Lantern": {
        "hi": "हाथ से रंगा मिट्टी का लालटेन",
        "mr": "हाताने रंगवलेला मातीचा कंदील",
    },
    "A rustic clay lantern with hand-painted details and cutouts, designed to hold a small candle or light.": {
        "hi": "हाथ की चित्रकारी और कटाव वाला देहाती मिट्टी का लालटेन, छोटी मोमबत्ती या रोशनी रखने के लिए।",
        "mr": "हस्तचित्रांची नक्षी आणि छिद्रे असलेला ग्रामीण ढंगाचा मातीचा कंदील, छोटी मेणबत्ती किंवा दिवा ठेवण्यासाठी.",
    },
    "Decorative Bird Figurines on a Log": {
        "hi": "लकड़ी के लट्ठे पर सजावटी चिड़ियों की मूर्तियाँ",
        "mr": "लाकडी ओंडक्यावर पक्ष्यांच्या सजावटी मूर्ती",
    },
    "A decorative piece featuring several small, colorful bird figurines perched on a natural piece of wood or log.": {
        "hi": "प्राकृतिक लकड़ी के टुकड़े पर बैठी कई रंगीन छोटी चिड़ियों की मूर्तियों वाली सजावटी वस्तु।",
        "mr": "नैसर्गिक लाकडाच्या तुकड्यावर बसवलेल्या अनेक रंगीत छोट्या पक्ष्यांच्या मूर्तींची सजावटी वस्तू.",
    },
    "Ceramic Plate with Leaf Impression": {
        "hi": "पत्ती की छाप वाली सिरेमिक प्लेट",
        "mr": "पानाचा ठसा असलेली सिरॅमिक प्लेट",
    },
    "A decorative ceramic plate with an impressed leaf pattern and a light green glaze.": {
        "hi": "पत्ती की उभरी छाप और हल्की हरी चमकदार परत वाली सजावटी सिरेमिक प्लेट।",
        "mr": "पानाचा उठावदार ठसा आणि फिकट हिरव्या झिलईची सजावटी सिरॅमिक प्लेट.",
    },
    "Hand-Painted Terracotta Pot": {
        "hi": "हाथ से रंगा टेराकोटा गमला",
        "mr": "हाताने रंगवलेली मातीची कुंडी",
    },
    "Hand-painted Terracotta Pot": {
        "hi": "हाथ से रंगा टेराकोटा गमला",
        "mr": "हाताने रंगवलेली मातीची कुंडी",
    },
    "A small terracotta pot with a delicate floral design hand-painted on a white background.": {
        "hi": "सफेद पृष्ठभूमि पर नाज़ुक फूलों की हाथ की चित्रकारी वाला छोटा टेराकोटा गमला।",
        "mr": "पांढऱ्या पार्श्वभूमीवर नाजूक फुलांची नक्षी हाताने रंगवलेली छोटी मातीची कुंडी.",
    },
    "Traditional Wooden & Metal Wall Clock": {
        "hi": "पारंपरिक लकड़ी और धातु की दीवार घड़ी",
        "mr": "पारंपरिक लाकूड आणि धातूचे भिंतीवरील घड्याळ",
    },
    "A large, traditional-style wall clock with a distressed wooden frame and a metal clock face.": {
        "hi": "पुराने रूप के लकड़ी फ्रेम और धातु के डायल वाली बड़ी पारंपरिक दीवार घड़ी।",
        "mr": "जुन्या पोताची लाकडी चौकट आणि धातूचा डायल असलेले मोठे पारंपरिक भिंतीवरील घड्याळ.",
    },
    "Set of Miniature Clay Pots (Colored)": {
        "hi": "रंगीन छोटी मिट्टी की मटकियाँ (सेट)",
        "mr": "रंगीत छोट्या मातीच्या कुंड्या (संच)",
    },
    "A set of small clay pots in different shapes, painted in vibrant colors.": {
        "hi": "अलग-अलग आकार की छोटी मिट्टी की मटकियाँ, चटख रंगों में रंगी हुई।",
        "mr": "वेगवेगळ्या आकारांच्या छोट्या मातीच्या कुंड्या उठावदार रंगांनी रंगवलेल्या आहेत.",
    },
    "Hand-painted Terracotta Water Pitcher": {
        "hi": "हाथ से रंगा टेराकोटा पानी का घड़ा",
        "mr": "हाताने रंगवलेले मातीचे पाण्याचे माठ",
    },
    "A traditional terracotta water pitcher with a colorful, hand-painted peacock design.": {
        "hi": "रंगीन मोर की हाथ की चित्रकारी वाला पारंपरिक टेराकोटा पानी का घड़ा।",
        "mr": "रंगीत मोराची नक्षी हाताने रंगवलेला पारंपरिक मातीचा पाण्याचा माठ.",
    },
    "Intricate Carved Wooden Panel": {
        "hi": "बारीक नक्काशी वाला लकड़ी का पैनल",
        "mr": "नाजूक कोरीव कामाचा लाकडी पॅनेल",
    },
    "A detailed, hand-carved wooden panel featuring a complex geometric pattern.": {
        "hi": "जटिल ज्यामितीय नक्काशी वाला बारीक हाथ से तराशा गया लकड़ी का पैनल।",
        "mr": "गुंतागुंतीची भौमितिक नक्षी हाताने कोरलेला तपशीलवार लाकडी पॅनेल.",
    },
    "Decorative Clay & Twine Vase": {
        "hi": "मिट्टी और सुतली का सजावटी फूलदान",
        "mr": "माती आणि सुतळीची सजावटी फुलदाणी",
    },
    "A unique decorative vase with a natural clay base and a top wrapped in twine for a rustic feel.": {
        "hi": "प्राकृतिक मिट्टी के आधार और देहाती रूप के लिए सुतली से लिपटे ऊपरी हिस्से वाला अनोखा फूलदान।",
        "mr": "नैसर्गिक मातीचा तळ आणि ग्रामीण लुकसाठी सुतळीने गुंडाळलेला वरचा भाग असलेली अनोखी फुलदाणी.",
    },
    "Assorted Decorative Vases": {
        "hi": "विविध सजावटी फूलदान",
        "mr": "विविध सजावटी फुलदाण्या",
    },
    "A collection of assorted small vases in different materials and colors, perfect for a shelf display.": {
        "hi": "अलग-अलग सामग्री और रंगों के छोटे फूलदानों का संग्रह, शेल्फ पर सजाने के लिए।",
        "mr": "वेगवेगळ्या साहित्यांची आणि रंगांची छोटी फुलदाणी शेल्फवर सजवण्यासाठी सुंदर आहेत.",
    },
    "Terracotta Flower Pot with a Hand-painted Design": {
        "hi": "हाथ से रंगे डिज़ाइन वाला टेराकोटा गमला",
        "mr": "हाताने रंगवलेल्या नक्षीची मातीची फुलकुंडी",
    },
    "A simple terracotta flower pot adorned with a hand-painted black and white pattern.": {
        "hi": "काले-सफेद पैटर्न की हाथ की चित्रकारी से सजा साधारण टेराकोटा फूलदान।",
        "mr": "काळ्या-पांढऱ्या नक्षीने हाताने रंगवलेली साधी मातीची फुलकुंडी.",
    },
    "Hand-painted Kettle with Floral Design": {
        "hi": "फूलों के डिज़ाइन वाली हाथ से रंगी केतली",
        "mr": "फुलांच्या नक्षीची हाताने रंगवलेली केतली",
    },
    "A metal kettle with a vibrant and detailed hand-painted floral pattern, a perfect decorative accent.": {
        "hi": "चटख रंगों की बारीक हाथ की फूलकारी वाली धातु की केतली, सजावट के लिए खास।",
        "mr": "उठावदार रंगांची नाजूक फुलांची हस्तचित्रे असलेली धातूची केतली, सजावटीसाठी खास.",
    },
    "Set of Wooden Wall Planters": {
        "hi": "लकड़ी के दीवार गमलों का सेट",
        "mr": "लाकडी भिंतीवरील कुंड्यांचा संच",
    },
    "A set of wooden wall-mounted planters in a triangular shape, ideal for succulents or small air plants.": {
        "hi": "त्रिकोण आकार के लकड़ी के दीवार गमले, सक्यूलेंट या छोटे एयर प्लांट लगाने के लिए।",
        "mr": "त्रिकोणी आकाराच्या लाकडी भिंतीवरील कुंड्या, सक्युलंट्स किंवा छोट्या एअर प्लांट्ससाठी योग्य.",
    },
    "Hand-painted Terracotta Tray": {
        "hi": "हाथ से रंगी टेराकोटा ट्रे",
        "mr": "हाताने रंगवलेली मातीची ट्रे",
    },
    "A rectangular terracotta tray with a black and white geometric pattern, perfect for serving or as a decorative piece.": {
        "hi": "काले-सफेद ज्यामितीय पैटर्न वाली आयताकार टेराकोटा ट्रे, परोसने या सजाने के लिए।",
        "mr": "काळ्या-पांढऱ्या भौमितिक नक्षीची आयताकृती मातीची ट्रे, पदार्थ वाढण्यासाठी किंवा सजावटीसाठी.",
    },
    "Ceramic Bowl with Textured Finish": {
        "hi": "बनावटदार फिनिश वाला सिरेमिक कटोरा",
        "mr": "पोतदार फिनिशचा सिरॅमिक बाऊल",
    },
    "A small, deep ceramic bowl with a unique textured outer surface and a smooth, dark blue glazed interior.": {
        "hi": "अनोखी बनावट वाली बाहरी सतह और गहरे नीले चिकने ग्लेज़ वाले अंदरूनी भाग का छोटा, गहरा सिरेमिक कटोरा।",
        "mr": "वेगळ्या पोताचा बाहेरील भाग आणि गडद निळी गुळगुळीत झिलई असलेला आतला भाग असलेला छोटा खोल सिरॅमिक बाऊल.",
    },
    "Resin Wall Art with Gold Flakes": {
        "hi": "सुनहरी पत्तियों वाली रेज़िन दीवार कला",
        "mr": "सोनेरी कणांची रेझिन भिंतीवरील कलाकृती",
    },
    "A modern wall art piece made of resin with a marble-like effect and embedded gold flakes.": {
        "hi": "संगमरमर जैसे प्रभाव और जड़े हुए सुनहरे कणों वाली आधुनिक रेज़िन दीवार कलाकृति।",
        "mr": "संगमरवरासारखा प्रभाव आणि जडवलेले सोनेरी कण असलेली आधुनिक रेझिन भिंतीवरील कलाकृती.",
    },
    "Hand-painted Terracotta Serving Pot": {
        "hi": "हाथ से रंगा टेराकोटा परोसने का पात्र",
        "mr": "हाताने रंगवलेले मातीचे वाढण्याचे भांडे",
    },
    "A small terracotta pot with a lid, hand-painted with a simple yet elegant design.": {
        "hi": "ढक्कन वाला छोटा टेराकोटा पात्र, सरल लेकिन सुरुचिपूर्ण डिज़ाइन से हाथ से रंगा हुआ।",
        "mr": "साध्या पण देखण्या नक्षीने हाताने रंगवलेले झाकणाचे छोटे मातीचे भांडे.",
    },
    "Carved Wooden Elephant Head": {
        "hi": "नक्काशीदार लकड़ी का हाथी-मुख",
        "mr": "कोरीव लाकडी हत्तीचे मुख",
    },
    "A magnificent, hand-carved wooden elephant head wall mount, perfect for a statement wall.": {
        "hi": "दीवार को खास रूप देने के लिए हाथ से तराशा गया भव्य लकड़ी का हाथी-मुख।",
        "mr": "भिंतीला उठाव देणारे हाताने कोरलेले भव्य लाकडी हत्तीचे मुख.",
    },
    "A small resin idol of Lord Ganesha, seated on a base, with a metallic finish and intricate details.": {
        "hi": "आधार पर विराजमान भगवान गणेश की छोटी रेज़िन मूर्ति, धातुई फिनिश और बारीक विवरणों के साथ।",
        "mr": "आधारावर विराजमान भगवान गणेशाची छोटी रेझिन मूर्ती, धातूच्या झळाळीच्या फिनिश आणि नाजूक तपशीलांसह.",
    },
    "Hand-painted Terracotta Wind Chime": {
        "hi": "हाथ से रंगा टेराकोटा विंड चाइम",
        "mr": "हाताने रंगवलेले मातीचे विंड चाइम",
    },
    "A rustic wind chime made from small terracotta pieces with a hand-painted floral design.": {
        "hi": "छोटे टेराकोटा टुकड़ों से बना देहाती विंड चाइम, जिस पर फूलों की चित्रकारी हाथ से की गई है।",
        "mr": "छोट्या मातीच्या तुकड्यांपासून बनवलेले ग्रामीण ढंगाचे विंड चाइम, त्यावर फुलांची नक्षी हाताने रंगवली आहे.",
    },
    "Hand-painted Bird House": {
        "hi": "हाथ से रंगा पक्षीघर",
        "mr": "हाताने रंगवलेले पक्ष्यांचे घरटे",
    },
    "A small, hand-painted wooden birdhouse with a colorful and inviting design.": {
        "hi": "रंगीन और आकर्षक डिज़ाइन वाला हाथ से रंगा छोटा लकड़ी का पक्षीघर।",
        "mr": "रंगीत आणि आकर्षक नक्षीचे हाताने रंगवलेले छोटे लाकडी पक्ष्यांचे घरटे.",
    },
    "Resin & Wood Coaster Set": {
        "hi": "रेज़िन और लकड़ी के कोस्टर का सेट",
        "mr": "रेझिन आणि लाकडाच्या कोस्टरचा संच",
    },
    "A set of coasters combining the natural look of wood with a colorful resin design.": {
        "hi": "लकड़ी के प्राकृतिक रूप और रंगीन रेज़िन डिज़ाइन का मेल वाले कोस्टरों का सेट।",
        "mr": "लाकडाचा नैसर्गिक लुक आणि रंगीत रेझिन नक्षी यांचा संगम असलेला कोस्टर संच.",
    },
    "Hand-painted Terracotta Vase": {
        "hi": "हाथ से रंगा टेराकोटा फूलदान",
        "mr": "हाताने रंगवलेली मातीची फुलदाणी",
    },
    "A rustic terracotta vase with a wide mouth and a simple, hand-painted floral pattern.": {
        "hi": "चौड़े मुँह और सरल हाथ की फूलकारी वाले देहाती टेराकोटा फूलदान।",
        "mr": "रुंद तोंडाची आणि साध्या हस्तचित्रित फुलांच्या नक्षीची ग्रामीण ढंगाची मातीची फुलदाणी.",
    },
    "Wooden Wall Art with Terracotta Plates": {
        "hi": "टेराकोटा प्लेटों वाली लकड़ी की दीवार कला",
        "mr": "मातीच्या प्लेट्ससह लाकडी भिंतीवरील कलाकृती",
    },
    "A unique wall decor piece featuring a dark wooden frame holding three small, hand-painted terracotta plates.": {
        "hi": "गहरे लकड़ी के फ्रेम में हाथ से रंगी तीन छोटी टेराकोटा प्लेटों वाली अनोखी दीवार सजावट।",
        "mr": "गडद लाकडी चौकटीत हाताने रंगवलेल्या तीन छोट्या मातीच्या प्लेट्स असलेली अनोखी भिंतीवरील सजावट.",
    },
    "Hand-painted Terracotta Plate Set": {
        "hi": "हाथ से रंगी टेराकोटा प्लेटों का सेट",
        "mr": "हाताने रंगवलेल्या मातीच्या प्लेट्सचा संच",
    },
    "A set of two decorative terracotta plates, each with a different hand-painted design in blue and red.": {
        "hi": "दो सजावटी टेराकोटा प्लेटों का सेट, हर प्लेट पर नीले और लाल रंग का अलग हाथ से बना डिज़ाइन।",
        "mr": "दोन सजावटी मातीच्या प्लेट्सचा संच; प्रत्येकावर निळ्या आणि लाल रंगांची वेगळी हस्तचित्रित नक्षी आहे.",
    },
    "Small Decorative Clay Bell": {
        "hi": "छोटी सजावटी मिट्टी की घंटी",
        "mr": "छोटी सजावटी मातीची घंटा",
    },
    "A small, handcrafted clay bell with an intricate cutout design.": {
        "hi": "बारीक कटाव वाली हाथ से बनी छोटी मिट्टी की घंटी।",
        "mr": "नाजूक छिद्रांच्या नक्षीची हाताने बनवलेली छोटी मातीची घंटा.",
    },
    "Decorative Miniature Clay Pots (Abstract)": {
        "hi": "अमूर्त डिज़ाइन वाली छोटी सजावटी मिट्टी की मटकियाँ",
        "mr": "अमूर्त नक्षीच्या छोट्या सजावटी मातीच्या कुंड्या",
    },
    "A set of two small, decorative clay pots with abstract, artistic paint strokes.": {
        "hi": "अमूर्त कलात्मक रंग-रेखाओं वाली दो छोटी सजावटी मिट्टी की मटकियाँ।",
        "mr": "अमूर्त कलात्मक रंगरेषा असलेल्या दोन छोट्या सजावटी मातीच्या कुंड्या.",
    },
    "Hand-painted Clay Pot with Handles": {
        "hi": "हैंडल वाला हाथ से रंगा मिट्टी का पात्र",
        "mr": "हाताळ्यांचे हाताने रंगवलेले मातीचे भांडे",
    },
    "A small clay pot with a handle on each side, featuring a hand-painted design of a bird and flowers.": {
        "hi": "दोनों ओर हैंडल वाला छोटा मिट्टी का पात्र, जिस पर पक्षी और फूल हाथ से बनाए गए हैं।",
        "mr": "दोन्ही बाजूंना हाताळे असलेल्या छोट्या मातीच्या भांड्यावर पक्षी आणि फुले हाताने रंगवली आहेत.",
    },
    "Hand-painted Wooden Wall Plate": {
        "hi": "हाथ से रंगी लकड़ी की दीवार प्लेट",
        "mr": "हाताने रंगवलेली लाकडी भिंतीवरील प्लेट",
    },
    "A circular wooden wall plate with a detailed hand-painted scene of a village and a person.": {
        "hi": "गाँव और एक व्यक्ति के विस्तृत हाथ से रंगे दृश्य वाली गोल लकड़ी की दीवार प्लेट।",
        "mr": "गाव आणि एका व्यक्तीचे तपशीलवार हस्तचित्र असलेली गोल लाकडी भिंतीवरील प्लेट.",
    },
    "Set of Hand-painted Terracotta Cups": {
        "hi": "हाथ से रंगे टेराकोटा कप (सेट)",
        "mr": "हाताने रंगवलेले मातीचे कप (संच)",
    },
    "A set of two small terracotta cups with simple, hand-painted designs, ideal for tea or as decor.": {
        "hi": "सरल हाथ की चित्रकारी वाले दो छोटे टेराकोटा कप, चाय या सजावट के लिए।",
        "mr": "साधी हस्तचित्रित नक्षी असलेले दोन छोटे मातीचे कप, चहा किंवा सजावटीसाठी योग्य.",
    },
    "Rustic Wooden Plant Stand": {
        "hi": "देहाती लकड़ी का पौधा-स्टैंड",
        "mr": "ग्रामीण ढंगाचा लाकडी रोप-स्टँड",
    },
    "A handcrafted wooden plant stand with a natural, unfinished look, perfect for a single pot.": {
        "hi": "प्राकृतिक, बिना पॉलिश रूप वाला हस्तनिर्मित लकड़ी का पौधा-स्टैंड, एक गमले के लिए।",
        "mr": "नैसर्गिक, अपूर्ण फिनिशचा हाताने बनवलेला लाकडी रोप-स्टँड एका कुंडीसाठी योग्य.",
    },
    "Hand-painted Terracotta Jug": {
        "hi": "हाथ से रंगा टेराकोटा घड़ा",
        "mr": "हाताने रंगवलेला मातीचा माठ",
    },
    "A large terracotta jug with a handle, featuring a vibrant hand-painted pattern around the body.": {
        "hi": "हैंडल वाला बड़ा टेराकोटा घड़ा, जिसके शरीर पर चटख पैटर्न हाथ से रंगा गया है।",
        "mr": "हाताळा असलेल्या मोठ्या मातीच्या माठावर उठावदार नक्षी हाताने रंगवली आहे.",
    },
    "Textured Terracotta Vase": {
        "hi": "बनावटदार टेराकोटा फूलदान",
        "mr": "पोतदार मातीची फुलदाणी",
    },
    "A medium-sized terracotta vase with a rough, textured finish and a natural, unpainted look.": {
        "hi": "खुरदरी बनावट और प्राकृतिक, बिना रंगे रूप वाला मध्यम आकार का टेराकोटा फूलदान।",
        "mr": "खडबडीत पोत आणि नैसर्गिक, न रंगवलेला लुक असलेली मध्यम आकाराची मातीची फुलदाणी.",
    },
    "Decorative Miniature Pots with a Rope Accent": {
        "hi": "रस्सी की सजावट वाली छोटी मटकियाँ",
        "mr": "दोरीच्या सजावटीची छोटी मातीची भांडी",
    },
    "A set of two small, decorative clay pots with a simple, solid color and a rope tied around the neck.": {
        "hi": "एकसमान रंग और गर्दन पर बँधी रस्सी वाली दो छोटी सजावटी मिट्टी की मटकियाँ।",
        "mr": "एकाच रंगाची आणि मानेभोवती दोरी बांधलेली दोन छोटी सजावटी मातीची भांडी.",
    },
    "Hand-painted Terracotta Plate": {
        "hi": "हाथ से रंगी टेराकोटा प्लेट",
        "mr": "हाताने रंगवलेली मातीची प्लेट",
    },
    "A decorative terracotta plate with a rustic finish and a hand-painted design of a bird in a cage.": {
        "hi": "देहाती फिनिश वाली सजावटी टेराकोटा प्लेट, जिस पर पिंजरे में पक्षी का चित्र हाथ से बनाया गया है।",
        "mr": "पिंजऱ्यातील पक्ष्याचे चित्र हाताने रंगवलेली ग्रामीण पोताची सजावटी मातीची प्लेट.",
    },
    "Hand-carved Wooden Coaster Set": {
        "hi": "हाथ से नक्काशी किए लकड़ी के कोस्टर",
        "mr": "हाताने कोरलेल्या लाकडी कोस्टरचा संच",
    },
    "A set of wooden coasters with an intricate, hand-carved floral pattern.": {
        "hi": "बारीक हाथ की फूलों वाली नक्काशी के लकड़ी के कोस्टरों का सेट।",
        "mr": "नाजूक फुलांची नक्षी हाताने कोरलेल्या लाकडी कोस्टरचा संच.",
    },
    "Hand-painted Decorative Box": {
        "hi": "हाथ से रंगा सजावटी डिब्बा",
        "mr": "हाताने रंगवलेली सजावटी पेटी",
    },
    "A small, hand-painted wooden box with a vibrant, detailed design on the lid.": {
        "hi": "ढक्कन पर चटख और बारीक डिज़ाइन वाला हाथ से रंगा छोटा लकड़ी का डिब्बा।",
        "mr": "झाकणावर उठावदार आणि नाजूक नक्षी असलेली हाताने रंगवलेली छोटी लाकडी पेटी.",
    },
    "Terracotta Flower Pot with a Hand-painted Pattern": {
        "hi": "हाथ से रंगे पैटर्न वाला टेराकोटा गमला",
        "mr": "हाताने रंगवलेल्या नक्षीची मातीची फुलकुंडी",
    },
    "A classic terracotta flower pot with a simple, hand-painted geometric pattern in black.": {
        "hi": "काले रंग की सरल ज्यामितीय हाथ की चित्रकारी वाला पारंपरिक टेराकोटा गमला।",
        "mr": "काळ्या रंगाची साधी भौमितिक नक्षी हाताने रंगवलेली पारंपरिक मातीची फुलकुंडी.",
    },
    "Decorative Clay Pots with Rope": {
        "hi": "रस्सी वाले सजावटी मिट्टी के गमले",
        "mr": "दोरीची सजावट असलेल्या मातीच्या कुंड्या",
    },
    "A set of small, decorative clay pots with a simple design and a thick rope handle.": {
        "hi": "सरल डिज़ाइन और मोटे रस्सी के हैंडल वाले छोटे सजावटी मिट्टी के गमलों का सेट।",
        "mr": "साधी नक्षी आणि जाड दोरीचे हाताळे असलेल्या छोट्या सजावटी मातीच्या कुंड्यांचा संच.",
    },
    "A decorative terracotta pot with a hand-painted scene of a village and a tree.": {
        "hi": "गाँव और पेड़ का दृश्य हाथ से रंगा हुआ सजावटी टेराकोटा गमला।",
        "mr": "गाव आणि झाडाचे दृश्य हाताने रंगवलेली सजावटी मातीची कुंडी.",
    },
    "Miniature Terracotta Jugs": {
        "hi": "छोटे टेराकोटा घड़े",
        "mr": "छोटे मातीचे माठ",
    },
    "A pair of small, decorative terracotta jugs with a rustic finish and intricate carvings.": {
        "hi": "देहाती फिनिश और बारीक नक्काशी वाले दो छोटे सजावटी टेराकोटा घड़े।",
        "mr": "ग्रामीण पोत आणि नाजूक कोरीव कामाचे दोन छोटे सजावटी मातीचे माठ.",
    },
    "Hand-painted Terracotta Plate with Floral Design": {
        "hi": "फूलों के डिज़ाइन वाली हाथ से रंगी टेराकोटा प्लेट",
        "mr": "फुलांच्या नक्षीची हाताने रंगवलेली मातीची प्लेट",
    },
    "A decorative terracotta plate with a simple, hand-painted floral motif in a rustic style.": {
        "hi": "देहाती अंदाज़ में सरल फूलों की हाथ की चित्रकारी वाली सजावटी टेराकोटा प्लेट।",
        "mr": "ग्रामीण शैलीतील साधी फुलांची नक्षी हाताने रंगवलेली सजावटी मातीची प्लेट.",
    },
    "A rectangular wooden wall hanging with a hand-painted scene of a rustic landscape.": {
        "hi": "देहाती प्राकृतिक दृश्य की हाथ से बनी चित्रकारी वाली आयताकार लकड़ी की दीवार सजावट।",
        "mr": "ग्रामीण निसर्गदृश्य हाताने रंगवलेली आयताकृती लाकडी भिंतीवरील सजावट.",
    },
    "A collection of small, unpainted clay pots in various shapes and sizes, suitable for small plants or display.": {
        "hi": "अलग-अलग आकारों की बिना रंगी छोटी मिट्टी की मटकियाँ, नन्हे पौधों या सजावट के लिए।",
        "mr": "वेगवेगळ्या आकारांच्या न रंगवलेल्या छोट्या मातीच्या कुंड्या, लहान रोपे किंवा सजावटीसाठी.",
    },
    "Decorative Hanging Terracotta Bird": {
        "hi": "सजावटी टेराकोटा पक्षी लटकन",
        "mr": "सजावटी मातीचा पक्षी लटकन",
    },
    "A decorative hanging ornament of a bird, handcrafted from terracotta with hand-painted details.": {
        "hi": "टेराकोटा से बना हाथ से रंगे विवरणों वाला पक्षी की आकृति का सजावटी लटकन।",
        "mr": "मातीपासून बनवलेल्या पक्ष्याच्या आकाराच्या सजावटी लटकनावर तपशील हाताने रंगवले आहेत.",
    },
    "A decorative terracotta pot with a unique hand-painted design and a natural, unglazed finish.": {
        "hi": "अनूठी हाथ की चित्रकारी और प्राकृतिक बिना ग्लेज़ की फिनिश वाला सजावटी टेराकोटा गमला।",
        "mr": "अनोखी हस्तचित्रित नक्षी आणि नैसर्गिक, झिलई न केलेली फिनिश असलेली सजावटी मातीची कुंडी.",
    },
    "Hand-carved Wooden Wall Art": {
        "hi": "हाथ से नक्काशी की लकड़ी की दीवार कला",
        "mr": "हाताने कोरलेली लाकडी भिंतीवरील कलाकृती",
    },
    "A round, hand-carved wooden wall art piece featuring a detailed mandala-like pattern.": {
        "hi": "मंडला जैसी बारीक नक्काशी वाला गोल हाथ से तराशा गया लकड़ी का दीवार-अलंकरण।",
        "mr": "मंडलासारखी तपशीलवार नक्षी हाताने कोरलेली गोल लाकडी भिंतीवरील कलाकृती.",
    },
}


class TranslationRequest(BaseModel):
    language: Literal["hi", "mr"]
    texts: list[str] = Field(min_length=1, max_length=100)


class TranslationResponse(BaseModel):
    translations: list[str]


def _translate_texts(texts: list[str], language: str) -> list[str]:
    translated: dict[str, str] = {}
    for text in texts:
        reviewed_translation = _CURATED_PRODUCT_TRANSLATIONS.get(text, {}).get(language)
        if reviewed_translation is not None:
            translated[text] = reviewed_translation
    missing_texts = [text for text in dict.fromkeys(texts) if text not in translated]
    if not missing_texts:
        return [translated[text] for text in texts]

    api_key = os.getenv("GOOGLE_CLOUD_TRANSLATE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Google Cloud Translation is not configured for unreviewed product text.",
        )

    machine_translations = _google_translate(missing_texts, language, api_key)
    translated.update(zip(missing_texts, machine_translations))
    return [translated[text] for text in texts]


def _google_translate(texts: list[str], language: str, api_key: str) -> list[str]:
    url = "https://translation.googleapis.com/language/translate/v2?" + urlencode({"key": api_key})
    request = URLRequest(
        url,
        data=json.dumps({"q": texts, "target": language, "format": "text"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Google Cloud Translation rejected the request (HTTP {error.code}).",
        ) from error
    except URLError as error:
        raise HTTPException(
            status_code=502,
            detail="Google Cloud Translation could not be reached.",
        ) from error
    except TimeoutError as error:
        raise HTTPException(
            status_code=504,
            detail="Google Cloud Translation timed out.",
        ) from error
    except OSError as error:
        raise HTTPException(
            status_code=502,
            detail="Google Cloud Translation could not be reached.",
        ) from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise HTTPException(
            status_code=502,
            detail="Google Cloud Translation returned an invalid response.",
        ) from error

    results = payload.get("data", {}).get("translations") if isinstance(payload, dict) else None
    if (
        not isinstance(results, list)
        or len(results) != len(texts)
        or any(
            not isinstance(item, dict)
            or not isinstance(item.get("translatedText"), str)
            or not item["translatedText"].strip()
            for item in results
        )
    ):
        raise HTTPException(
            status_code=502,
            detail="Google Cloud Translation returned an incomplete response.",
        )
    return [html.unescape(item["translatedText"]) for item in results]


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
        translated_texts = await asyncio.to_thread(
            _translate_texts,
            missing_texts,
            body.language,
        )
        translations_by_text.update(zip(missing_texts, translated_texts))
        with _translation_cache_lock:
            for text, translated_text in zip(missing_texts, translated_texts):
                cache_key = (body.language, text)
                _translation_cache[cache_key] = translated_text
                while len(_translation_cache) > MAX_CACHED_TRANSLATIONS:
                    _translation_cache.popitem(last=False)

    translated_texts = [translations_by_text[text] for text in body.texts]
    return TranslationResponse(translations=translated_texts)
