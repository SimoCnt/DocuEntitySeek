/**
 * Render the public comparison card for a subscription plan.
 */

/**
 * Properties configuring the plan card component.
 */
type PlanCardProps = {
    name: string
    description: string
    features: string[]
    highlighted?: boolean
}


/**
 * Display the entitlement comparison for a subscription plan.
 */
function PlanCard({name, description, features, highlighted = false}: PlanCardProps) {    
    const className = highlighted
        ? 'plan-card plan-card--highlighted'   // SE highlighted è true usa "plan-card plan-card--highlighted"
        : 'plan-card'   // ALTRIMENTI usa "plan-card"

    return (
        <article className={className}>
            <h3>{name}</h3>
            <p>{description}</p>
            <ul>
                {features.map((feature) => (
                    <li key={feature}>{feature}</li>
                ))}
            </ul>
        </article>
    )
}

export default PlanCard
