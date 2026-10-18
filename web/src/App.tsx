import { AnimatePresence, motion } from 'motion/react'
import { Suspense, lazy, useEffect } from 'react'
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
  useEffect(() => {
    if (hash) {
      const t = setTimeout(() => document.getElementById(hash.slice(1))?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 350)
      return () => clearTimeout(t)
    }
    window.scrollTo({ top: 0 })
  }, [pathname, hash])
  return null
}

const TITLES: Record<string, string> = {
  '/': 'CropTransfer AT · Ein Feld. Viele Unterschiede. Endlich sichtbar.',
  '/contribute': 'Feld eintragen · CropTransfer AT',
  '/analyse': 'Feld analysieren · CropTransfer AT',
  '/evidence': 'Belege · CropTransfer AT',
  '/model': 'Modellsteckbrief · CropTransfer AT',
  '/data': 'Daten · CropTransfer AT',
  '/method': 'Methode · CropTransfer AT',
  '/about': 'Über das Projekt · CropTransfer AT',
}

export default function App() {
  const location = useLocation()
  useEffect(() => {
    document.title = TITLES[location.pathname] ?? 'CropTransfer AT'
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
