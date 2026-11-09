import './App.css'
import Header from './components/Header'
import HeroSection from './components/HeroSection'
import FeaturesSection from './components/FeaturesSection'
import AnalysisDemoSection from './components/analysis/AnalysisDemoSection'
import PlansSection from './components/PlansSection'
import Footer from './components/Footer'


function App() {
  return (
    <>
      <Header />

      <main>
        <HeroSection />
        <FeaturesSection />
        <AnalysisDemoSection />
        <PlansSection />
      </main>

      <Footer />
    </>
  )
}

export default App