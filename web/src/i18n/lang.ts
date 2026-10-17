/** Supported UI languages; German is the default. */
export const LANGS = [
  { code: 'de', label: 'Deutsch', short: 'DE', intl: 'de-AT' },
  { code: 'en', label: 'English', short: 'EN', intl: 'en-GB' },
  { code: 'es', label: 'Español', short: 'ES', intl: 'es-ES' },
  { code: 'fr', label: 'Français', short: 'FR', intl: 'fr-FR' },
] as const

export type LangCode = (typeof LANGS)[number]['code']

export const DEFAULT_LANG: LangCode = 'de'

let current: LangCode = DEFAULT_LANG

export const currentLang = () => current
export const setCurrentLang = (l: LangCode) => {
  current = l
}
export const intlLocale = (l: LangCode = current) => LANGS.find((x) => x.code === l)?.intl ?? 'de-AT'
