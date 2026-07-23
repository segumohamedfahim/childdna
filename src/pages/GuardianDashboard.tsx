import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { StatusBadge } from '@/components/ui/StatusBadge'

export default function GuardianDashboard() {
  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="container mx-auto max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl font-bold text-primary mb-2">Mission Control</h1>
          <p className="text-gray-600 mb-8">Everything is Safe</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card>
              <h3 className="text-sm text-gray-500 mb-2">Children Registered</h3>
              <p className="text-3xl font-bold text-primary">0</p>
            </Card>
            
            <Card>
              <h3 className="text-sm text-gray-500 mb-2">Recent Rescue Sessions</h3>
              <p className="text-3xl font-bold text-primary">0</p>
            </Card>
            
            <Card>
              <h3 className="text-sm text-gray-500 mb-2">Mission Status</h3>
              <StatusBadge status="online" />
            </Card>
          </div>

          <div className="mb-8">
            <Button size="lg">Generate Child DNA Token</Button>
          </div>

          <Card>
            <h3 className="text-lg font-semibold text-primary mb-4">Timeline Preview</h3>
            <p className="text-gray-600">No active rescue sessions</p>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}