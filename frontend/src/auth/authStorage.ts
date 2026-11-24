/**
 * Persist the JWT access token for the current browser tab session.
 */

const ACCESS_TOKEN_KEY = 'docuentityseek.access-token'


/**
 * Read a previously stored token from browser session storage.
 */
export function getStoredAccessToken() {
    return sessionStorage.getItem(ACCESS_TOKEN_KEY)
}


/**
 * Store an access token for the current browser tab session.
 */
export function storeAccessToken(token: string) {
    sessionStorage.setItem(ACCESS_TOKEN_KEY, token)
}


/**
 * Remove the browser session token after logout or invalidation.
 */
export function clearStoredAccessToken() {
    sessionStorage.removeItem(ACCESS_TOKEN_KEY)
}
