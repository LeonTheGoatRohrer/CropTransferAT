import i18n from 'i18next'
import { initReactI18next, useTranslation } from 'react-i18next'
import { DEFAULT_LANG, LANGS, setCurrentLang, type LangCode } from './lang'
import de, { type Locale } from './locales/de'
import en from './locales/en'
import es from './locales/es'
import fr from './locales/fr'

export const LOCALES: Record<LangCode, Locale> = { de, en, es, fr }

const STORAGE_KEY = 'ct-lang'

function initialLang(): LangCode {
  try {
    const saved = localStorage.getItem(STORAGE_KEY) as LangCode | null
    if (saved && LANGS.some((l) => l.code === saved)) return saved
  } catch {
    /* storage unavailable */
  }
  return DEFAULT_LANG
}

const lng = initialLang()
setCurrentLang(lng)

i18n.use(initReactI18next).init({
  resources: Object.fromEntries(Object.entries(LOCALES).map(([k, v]) => [k, { translation: v.ui }])),
  lng,
  fallbackLng: DEFAULT_LANG,
  interpolation: { escapeValue: false },
  returnNull: false,
})

document.documentElement.lang = lng

i18n.on('languageChanged', (l) => {
  setCurrentLang(l as LangCode)
  document.documentElement.lang = l
  try {
    localStorage.setItem(STORAGE_KEY, l)
  } catch {
    /* ignore */
  }
})

/** Structured, typed content (lists, cards) of the current language. */
export function useContent(): Locale['content'] {
  const { i18n: inst } = useTranslation()
  return (LOCALES[inst.language as LangCode] ?? LOCALES[DEFAULT_LANG]).content
}

export default i18n
