import { Database, PenLine } from 'lucide-react'
import { ButtonLink } from '../ui/Button'

/** Two buttons at the top of the side panel: enter your own field, or open the prepared reference fields. */
export function ModeSwitch({ active }: { active: 'contribute' | 'analyse' }) {
  return (
    <div className="mb-6 grid grid-cols-2 gap-2">
      <ButtonLink to="/contribute" size="sm" variant={active === 'contribute' ? 'primary' : 'secondary'} icon={<PenLine className="size-3.5" />}>
        Feld eintragen
      </ButtonLink>
      <ButtonLink to="/analyse" size="sm" variant={active === 'analyse' ? 'primary' : 'secondary'} icon={<Database className="size-3.5" />}>
        Referenzfelder ansehen
      </ButtonLink>
    </div>
  )
}
