import { useEffect, useState } from "react";
import API from "../api";
import { useLanguage } from "./LanguageContext";

const translationCache = new Map();
const pendingTranslations = new Map();
let queuedTranslations = [];
let flushScheduled = false;
const TRANSLATION_CATALOG_VERSION = "reviewed-copy-v5";

const translationKey = (language, text) => JSON.stringify([TRANSLATION_CATALOG_VERSION, language, text]);

const scheduleTranslationFlush = () => {
  if (flushScheduled) return;
  flushScheduled = true;
  Promise.resolve().then(async () => {
    flushScheduled = false;
    const queued = queuedTranslations;
    queuedTranslations = [];

    const languageGroups = queued.reduce((groups, item) => {
      groups[item.language] = groups[item.language] || [];
      groups[item.language].push(item);
      return groups;
    }, {});

    await Promise.all(Object.entries(languageGroups).map(async ([language, items]) => {
      const batches = [];
      let batch = [];
      let batchCharacters = 0;

      items.forEach((item) => {
        if (batch.length === 100 || batchCharacters + item.text.length > 20000) {
          batches.push(batch);
          batch = [];
          batchCharacters = 0;
        }
        batch.push(item);
        batchCharacters += item.text.length;
      });
      if (batch.length) batches.push(batch);

      await Promise.all(batches.map(async (translationBatch) => {
        try {
          const response = await API.post("/translations", {
            language,
            texts: translationBatch.map((item) => item.text)
          });
          const translatedTexts = response.data?.translations;
          if (
            !Array.isArray(translatedTexts)
            || translatedTexts.length !== translationBatch.length
            || translatedTexts.some((text) => typeof text !== "string")
          ) {
            throw new Error("Translation service returned an invalid batch.");
          }

          translationBatch.forEach((item, index) => {
            translationCache.set(item.key, translatedTexts[index]);
            pendingTranslations.delete(item.key);
            item.resolve(translatedTexts[index]);
          });
        } catch (error) {
          translationBatch.forEach((item) => {
            pendingTranslations.delete(item.key);
            item.reject(error);
          });
        }
      }));
    }));

    if (queuedTranslations.length) scheduleTranslationFlush();
  });
};

const translateText = (text, language) => {
  const key = translationKey(language, text);
  if (translationCache.has(key)) return Promise.resolve(translationCache.get(key));
  if (pendingTranslations.has(key)) return pendingTranslations.get(key);

  const translation = new Promise((resolve, reject) => {
    queuedTranslations.push({ key, language, text, resolve, reject });
  });
  pendingTranslations.set(key, translation);
  scheduleTranslationFlush();
  return translation;
};

export const useTranslatedValues = (sourceValues) => {
  const { currentLang, t } = useLanguage();
  const valuesKey = JSON.stringify(sourceValues.map((value) => value || ""));
  const [result, setResult] = useState(() => ({
    values: currentLang === "en" ? JSON.parse(valuesKey) : [],
    isTranslating: currentLang !== "en",
    error: false,
    language: currentLang,
    valuesKey
  }));

  useEffect(() => {
    let active = true;
    const values = JSON.parse(valuesKey);
    if (currentLang === "en" || values.every((value) => !value)) {
      setResult({ values, isTranslating: false, error: false, language: currentLang, valuesKey });
      return () => { active = false; };
    }

    setResult({
      values: [],
      isTranslating: true,
      error: false,
      language: currentLang,
      valuesKey
    });
    Promise.all(values.map((value) => value ? translateText(value, currentLang) : Promise.resolve(value)))
      .then((translatedValues) => {
        if (active) {
          setResult({
            values: translatedValues,
            isTranslating: false,
            error: false,
            language: currentLang,
            valuesKey
          });
        }
      })
      .catch((error) => {
        console.error("Could not translate product information:", error);
        if (active) {
          setResult({
            values,
            isTranslating: false,
            error: true,
            language: currentLang,
            valuesKey
          });
        }
      });

    return () => { active = false; };
  }, [currentLang, valuesKey]);

  const resultIsCurrent = result.language === currentLang && result.valuesKey === valuesKey;
  const values = currentLang === "en"
    ? JSON.parse(valuesKey)
    : resultIsCurrent
      ? result.values
      : [];
  return {
    values,
    isTranslating: currentLang !== "en" && (!resultIsCurrent || result.isTranslating),
    error: resultIsCurrent && result.error,
    t
  };
};
