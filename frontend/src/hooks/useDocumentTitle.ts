/**
 * Update the browser page title for the active application screen.
 */

import { useEffect } from 'react'


/**
 * Synchronize the active screen title with the browser document title.
 */
function useDocumentTitle(title: string) {
  useEffect(() => {
    const previousTitle = document.title
    document.title = title
    return () => {
      document.title = previousTitle
    }
  }, [title])
}

export default useDocumentTitle
