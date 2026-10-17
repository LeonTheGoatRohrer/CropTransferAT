import { ArrowRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { ButtonLink } from '../components/ui/Button'
import { Container } from '../components/ui/Section'

export default function NotFound() {
  const { t } = useTranslation()
  return (
    <section className="flex min-h-[70vh] items-center pt-24">
      <Container>
        <p className="eyebrow mb-5">{t('notFound.eyebrow')}</p>
        <h1 className="max-w-[720px] text-[clamp(2.4rem,5vw,4rem)] leading-[1] tracking-[-0.04em]">{t('notFound.title')}</h1>
        <p className="mt-5 max-w-[520px] text-[16px] text-ink-2">{t('notFound.body')}</p>
        <div className="mt-9 flex flex-wrap gap-3">
          <ButtonLink to="/" variant="secondary">{t('nav.home')}</ButtonLink>
          <ButtonLink to="/analyse" icon={<ArrowRight className="size-4" />}>{t('nav.cta')}</ButtonLink>
        </div>
      </Container>
    </section>
  )
}
