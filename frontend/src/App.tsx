import { Route, Routes } from 'react-router'

import GuestRoute from './components/auth/GuestRoute'
import ProtectedRoute from './components/auth/ProtectedRoute'
import AppLayout from './components/layout/AppLayout'
import DocumentDetailPage from './pages/DocumentDetailPage'
import DocumentsPage from './pages/DocumentsPage'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import NewDocumentPage from './pages/NewDocumentPage'
import NotFoundPage from './pages/NotFoundPage'
import RegisterPage from './pages/RegisterPage'
import SchemasPage from './pages/SchemasPage'


function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<HomePage />} />

        <Route element={<GuestRoute />}>
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route path="documents" element={<DocumentsPage />} />
          <Route path="documents/new" element={<NewDocumentPage />} />
          <Route path="documents/:documentId" element={<DocumentDetailPage />} />
          <Route path="schemas" element={<SchemasPage />} />
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}

export default App