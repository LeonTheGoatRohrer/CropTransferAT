/**
 * Decorative full-bleed image behind a page header. The image sits to the right and
 * fades into the page colour on the left (where the text is) and at the bottom, so the
 * section blends into the next one. The image box is capped at one screen height, so a tall
 * section does not blow the image up. The parent section needs `relative isolate overflow-hidden`.
 * Images: AI-generated (Higgsfield), see SUPPORT.md; files in public/img/ (<name>-1280/-2560.webp).
 */
export function Backdrop({ name, position = 'right center', opacity = 1 }: { name: string; position?: string; opacity?: number }) {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
      <div className="absolute inset-x-0 top-0 h-full max-h-[min(100svh,1000px)]">
        <img
          src={`/img/${name}-2560.webp`}
          srcSet={`/img/${name}-1280.webp 1280w, /img/${name}-2560.webp 2560w`}
          sizes="100vw"
          alt=""
          decoding="async"
          className="absolute inset-0 size-full object-cover"
          style={{ objectPosition: position, opacity }}
        />
        {/* text side: strong on phones (text spans the width), lighter on wide screens */}
        <div className="absolute inset-0 bg-soil-950/75 md:bg-transparent md:bg-[linear-gradient(90deg,var(--color-soil-950)_0%,rgb(11_15_12/0.86)_34%,rgb(11_15_12/0.35)_62%,rgb(11_15_12/0.1)_100%)]" />
        {/* top under the nav, bottom into the page */}
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgb(11_15_12/0.55)_0%,transparent_22%,transparent_60%,var(--color-soil-950)_100%)]" />
      </div>
    </div>
  )
}
