import { ArrowRight } from 'lucide-react'
import { ButtonLink } from '../components/ui/Button'
import { Container } from '../components/ui/Section'

export default function NotFound() {
  return (
    <section className="flex min-h-[70vh] items-center pt-24">
      <Container>
        <p className="eyebrow mb-5">404 · no clear scene</p>
        <h1 className="max-w-[720px] text-[clamp(2.4rem,5vw,4rem)] leading-[1] tracking-[-0.04em]">This page has no observation.</h1>
        <p className="mt-5 max-w-[520px] text-[16px] text-ink-2">The address does not exist. Start from the overview or open a field.</p>
        <div className="mt-9 flex gap-3">
          <ButtonLink to="/" variant="secondary">Overview</ButtonLink>
          <ButtonLink to="/analyse" icon={<ArrowRight className="size-4" />}>Analyse a field</ButtonLink>
        </div>
      </Container>
    </section>
  )
}
