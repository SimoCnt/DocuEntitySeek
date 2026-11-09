import FeaturesSection from '../components/FeaturesSection'
import HeroSection from '../components/HeroSection'
import PlansSection from '../components/PlansSection'

import useDocumentTitle from '../hooks/useDocumentTitle'


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