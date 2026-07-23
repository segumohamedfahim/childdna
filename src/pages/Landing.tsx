import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Timeline } from '@/components/ui/Timeline'

const heroFeatures = [
  {
    id: 1,
    title: 'Child DNA Token',
    description: 'Privacy-first identity.',
  },
  {
    id: 2,
    title: 'REUNITE AI',
    description: 'Intelligent rescue coordination.',
  },
  {
    id: 3,
    title: 'Rescue Timeline',
    description: 'Every rescue step recorded.',
  },
  {
    id: 4,
    title: 'First Helper Protocol',
    description: 'Guided assistance.',
  },
  {
    id: 5,
    title: 'Verified Reunion',
    description: 'Trusted handover.',
  },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="mb-4 text-5xl font-bold text-primary md:text-6xl">
            Child DNA
          </h1>
          <p className="mb-2 text-lg text-gray-600">
            Powered by REUNITE AI
          </p>
          <p className="mb-12 text-xl text-gray-600 max-w-2xl mx-auto">
            Privacy-first Child Identity &<br />
            Rapid Reunion Platform
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link to="/guardian">
              <Button size="lg">Register Child</Button>
            </Link>
            <Button variant="outline" size="lg">
              Watch Demo
            </Button>
          </div>
        </motion.div>
      </section>

      {/* Hero Features - Floating Cards */}
      <section className="container mx-auto px-4 pb-20">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
          {heroFeatures.map((feature, index) => (
            <motion.div
              key={feature.id}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              whileHover={{ y: -10, transition: { duration: 0.2 } }}
            >
              <Card className="h-full text-center p-6 hover:shadow-xl transition-shadow">
                <div className="mb-4 text-3xl font-bold text-accent">{feature.id}</div>
                <h3 className="mb-2 font-semibold text-primary">{feature.title}</h3>
                <p className="text-sm text-gray-600">{feature.description}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Rescue Timeline */}
      <section className="container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.6 }}
        >
          <h2 className="text-center text-2xl font-bold text-primary mb-12">
            Rescue Timeline
          </h2>
          <Timeline />
        </motion.div>
      </section>
    </div>
  )
}