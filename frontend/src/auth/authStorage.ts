const ACCESS_TOKEN_KEY = 'docuentityseek.access-token'


export function getStoredAccessToken() {
    return sessionStorage.getItem(ACCESS_TOKEN_KEY)
}


export function storeAccessToken(token: string) {
    sessionStorage.setItem(ACCESS_TOKEN_KEY, token)
}


export function clearStoredAccessToken() {
    sessionStorage.removeItem(ACCESS_TOKEN_KEY)
}