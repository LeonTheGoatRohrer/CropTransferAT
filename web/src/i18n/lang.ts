/** Supported UI languages; German is the default. (es/fr were AI drafts without review; removed, see commit 6e57725.) */
export const LANGS = [
  { code: 'de', label: 'Deutsch', short: 'DE', intl: 'de-AT' },
  { code: 'en', label: 'English', short: 'EN', intl: 'en-GB' },
] as const

export type LangCode = (typeof LANGS)[number]['code']

export const DEFAULT_LANG: LangCode = 'de'

let current: LangCode = DEFAULT_LANG

export const currentLang = () => current
export const setCurrentLang = (l: LangCode) => {
  current = l
}
export const intlLocale = (l: LangCode = current) => LANGS.find((x) => x.code === l)?.intl ?? 'de-AT'
