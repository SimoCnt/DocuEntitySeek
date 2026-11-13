export type UserRole =
    | 'USER'
    | 'ADMIN'


export type PlanCode =
    | 'BASE'
    | 'PREMIUM'


export type PlanResponse = {
    code: PlanCode
    name: string
    dailyAnalysisLimit: number | null
    customSchemasEnabled: boolean
}


export type UserResponse = {
    id: string
    email: string
    role: UserRole
    plan: PlanResponse
    isActive: boolean
    createdAt: string
    lastLoginAt: string | null
}


export type RegisterRequest = {
    email: string
    password: string
}


export type TokenResponse = {
    access_token: string
    token_type: 'bearer'
    expires_in: number
}