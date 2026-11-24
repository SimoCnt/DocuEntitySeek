/**
 * Compose the public landing page sections.
 */

import FeaturesSection from '../components/FeaturesSection'
import HeroSection from '../components/HeroSection'
import PlansSection from '../components/PlansSection'

import useDocumentTitle from '../hooks/useDocumentTitle'


/**
 * Compose the public landing page from reusable marketing sections.
 */
function HomePage() {
    useDocumentTitle('DocuEntitySeek')

    return (
        <>
            <HeroSection />
            <FeaturesSection />
            <PlansSection />
        </>
    )
}

export default HomePage
