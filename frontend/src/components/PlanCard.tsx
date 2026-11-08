type PlanCardProps = {
    name: string
    description: string
    features: string[]
    highlighted?: boolean
}


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