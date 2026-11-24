/**
 * Render a short product capability description on the public homepage.
 */

/**
 * Properties configuring the feature card component.
 */
type FeatureCardProps = {
  title: string
  description: string
  badge: string
}


/**
 * Present one platform capability with a brief explanation.
 */
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
