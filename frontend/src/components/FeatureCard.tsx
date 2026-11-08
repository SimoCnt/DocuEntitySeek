type FeatureCardProps = {
  title: string
  description: string
  badge: string
}


function FeatureCard({title, description, badge}: FeatureCardProps) {
  return (
    <article className="feature-card">
      <span className="feature-card__badge">{badge}</span>
      <h3>{title}</h3>
      <p>{description}</p>
    </article>
  )
}

export default FeatureCard