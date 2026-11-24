/**
 * Compose the shared navigation, routed content, and footer.
 */

import { Outlet } from 'react-router'

import Footer from '../Footer'
import Header from '../Header'


/**
 * Wrap routed content with persistent application navigation and footer.
 */
function AppLayout() {
    return (
        <>
            <Header />

            <main className="app-main">
                <Outlet />
            </main>

            <Footer />
        </>
    )
}

export default AppLayout
