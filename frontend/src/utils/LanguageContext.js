import { createContext, useContext } from "react";
import { translations } from "./translations";

export const LanguageContext = createContext("en");

export const useLanguage = () => {
  const currentLang = useContext(LanguageContext);
  return {
    currentLang,
    t: translations[currentLang] || translations.en
  };
};
