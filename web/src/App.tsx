import { AnimatePresence, motion } from 'motion/react'
import { Suspense, lazy, useEffect, useRef } from 'react'
import { Route, Routes, useLocation } from 'react-router'
import { Footer } from './components/layout/Footer'
import { Nav } from './components/layout/Nav'

const Home = lazy(() => import('./pages/Home'))
const Contribute = lazy(() => import('./pages/Contribute'))
const Analyse = lazy(() => import('./pages/Analyse'))
const Evidence = lazy(() => import('./pages/Evidence'))
const ModelCard = lazy(() => import('./pages/ModelCard'))
const Data = lazy(() => import('./pages/Data'))
const Method = lazy(() => import('./pages/Method'))
const About = lazy(() => import('./pages/About'))
const NotFound = lazy(() => import('./pages/NotFound'))

function ScrollManager() {
  const { pathname, hash } = useLocation()
  const prevPath = useRef(pathname)
  useEffect(() => {
    // Jump straight to a section on another page; glide only within the current page.
    const behavior: ScrollBehavior = prevPath.current === pathname ? 'smooth' : 'auto'
    prevPath.current = pathname
    if (hash) {
      // The target page mounts only after the exit animation and its lazy chunk, and data
      // above the section can still shift it: poll for the anchor, then correct once.
      const id = hash.slice(1)
      let tries = 0
      let fix: ReturnType<typeof setTimeout> | undefined
      const poll = setInterval(() => {
        const el = document.getElementById(id)
        if (!el && ++tries < 40) return
        clearInterval(poll)
        if (!el) return
        el.scrollIntoView({ behavior, block: 'start' })
        fix = setTimeout(() => {
          const top = document.getElementById(id)?.getBoundingClientRect().top ?? 0
          if (Math.abs(top - 80) > 24) document.getElementById(id)?.scrollIntoView({ behavior: 'auto', block: 'start' })
        }, behavior === 'smooth' ? 1500 : 900)
      }, 100)
      return () => {
        clearInterval(poll)
        clearTimeout(fix)
      }
    }
    window.scrollTo({ top: 0 })
  }, [pathname, hash])
  return null
}

const TITLES: Record<string, string> = {
  '/': 'Delta Green · Ein Feld. Viele Unterschiede. Endlich sichtbar.',
  '/contribute': 'Feld eintragen · Delta Green',
  '/analyse': 'Feld analysieren · Delta Green',
  '/evidence': 'Belege · Delta Green',
  '/model': 'Modellsteckbrief · Delta Green',
  '/data': 'Daten · Delta Green',
  '/method': 'Methode · Delta Green',
  '/about': 'Über das Projekt · Delta Green',
}

export default function App() {
  const location = useLocation()
  useEffect(() => {
    document.title = TITLES[location.pathname] ?? 'Delta Green'
  }, [location.pathname])

  return (
    <div className="flex min-h-dvh flex-col">
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded-lg focus:bg-maize focus:px-3 focus:py-2 focus:text-soil-950">
        Zum Inhalt springen
      </a>
      <ScrollManager />
      <Nav />
      <main id="main" className="flex-1">
        <Suspense fallback={<div className="h-[70vh]" />}>
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
            >
              <Routes location={location}>
                <Route path="/" element={<Home />} />
                <Route path="/contribute" element={<Contribute />} />
                <Route path="/analyse" element={<Analyse />} />
                <Route path="/evidence" element={<Evidence />} />
                <Route path="/model" element={<ModelCard />} />
                <Route path="/data" element={<Data />} />
                <Route path="/method" element={<Method />} />
                <Route path="/about" element={<About />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </motion.div>
          </AnimatePresence>
        </Suspense>
      </main>
      {location.pathname !== '/analyse' && location.pathname !== '/contribute' && <Footer />}
    </div>
  )
}
