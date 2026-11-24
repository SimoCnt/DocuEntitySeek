/**
 * Define account, subscription, token, and quota request/response types.
 */

/**
 * TypeScript contract for user role values.
 */
export type UserRole =
    | 'USER'
    | 'ADMIN'


/**
 * TypeScript contract for plan code values.
 */
export type PlanCode =
    | 'BASE'
    | 'PREMIUM'


/**
 * Subscription capabilities displayed by the frontend.
 */
export type PlanResponse = {
    code: PlanCode
    name: string
    dailyAnalysisLimit: number | null
    customSchemasEnabled: boolean
}


/**
 * Public account profile including current role and subscription plan.
 */
export type UserResponse = {
    id: string
    email: string
    role: UserRole
    plan: PlanResponse
    isActive: boolean
    createdAt: string
    lastLoginAt: string | null
}


/**
 * Request payload for register operations.
 */
export type RegisterRequest = {
    email: string
    password: string
}


/**
 * Bearer access-token response returned after successful login.
 */
export type TokenResponse = {
    access_token: string
    token_type: 'bearer'
    expires_in: number
}


/**
 * Current plan limit, used capacity, and UTC reset timestamp.
 */
export type AnalysisQuotaResponse = {
    planCode: PlanCode
    dailyLimit: number | null
    usedOrReserved: number
    remaining: number | null
    resetsAt: string
    isUnlimited: boolean
}
