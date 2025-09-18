import { english } from './english';
import { italian } from './italian';

export const translations = {
  en: english,
  it: italian
};

export const getTranslation = (language = 'en') => {
  return translations[language] || translations['en'];
};