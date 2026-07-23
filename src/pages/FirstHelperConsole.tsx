import { motion } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'

const protocolSteps = [
  {
    id: 1,
    title: 'Identify',
    description: 'Recognize a child in need of help',
  },
  {
    id: 2,
    title: 'Activate',
    description: 'Use the Child DNA Token system',
  },
  {
    id: 3,
    title: 'Report',
    description: 'Provide location and details',
  },
  {
    id: 4,
    title: 'Assist',
    description: 'Follow guided protocol',
  },
]

export default function FirstHelperConsole() {
  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="container mx-auto max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <h1 className="text-2xl md:text-3xl font-bold text-primary mb-8">
            You may be the reason a child returns home safely.
          </h1>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Button size="lg">Activate Child DNA Token</Button>
            <Button variant="outline" size="lg">
              Report Child Without Token
            </Button>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          <h2 className="text-xl font-semibold text-primary mb-6 text-center">
            First Helper Protocol
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {protocolSteps.map((step, index) => (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.4 }}
              >
                <Card>
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                      {step.id}
                    </div>
                    <div>
                      <h3 className="font-semibold text-primary mb-1">{step.title}</h3>
                      <p className="text-sm text-gray-600">{step.description}</p>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}