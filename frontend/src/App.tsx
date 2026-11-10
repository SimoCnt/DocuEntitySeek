import { Route, Routes } from 'react-router'

import AppLayout from './components/layout/AppLayout'
import DocumentDetailPage from './pages/DocumentDetailPage'
import DocumentsPage from './pages/DocumentsPage'
import HomePage from './pages/HomePage'
import NotFoundPage from './pages/NotFoundPage'
import SchemasPage from './pages/SchemasPage'
import NewDocumentPage from './pages/NewDocumentPage'


function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route
          index
          element={<HomePage />}
        />

        <Route
          path="documents"
          element={<DocumentsPage />}
        />

        <Route
          path="documents/:documentId"
          element={<DocumentDetailPage />}
        />

        <Route
          path="schemas"
          element={<SchemasPage />}
        />

        <Route
          path="*"
          element={<NotFoundPage />}
        />
      </Route>

        <Route
          path="documents/new"
          element={<NewDocumentPage />}
        />
    </Routes>
  )
}

export default App