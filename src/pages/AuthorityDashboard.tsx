import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { StatusBadge } from '@/components/ui/StatusBadge'

export default function AuthorityDashboard() {
  return (
    <div className="min-h-screen bg-primary text-white p-4 md:p-8">
      <div className="container mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold">Authority Dashboard</h1>
            <StatusBadge status="active" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <Card className="bg-primary/50 border-gray-600">
              <h3 className="text-sm text-gray-300 mb-2">Active Incidents</h3>
              <p className="text-3xl font-bold">0</p>
            </Card>
            
            <Card className="bg-primary/50 border-gray-600">
              <h3 className="text-sm text-gray-300 mb-2">Today's Rescues</h3>
              <p className="text-3xl font-bold">0</p>
            </Card>
            
            <Card className="bg-primary/50 border-gray-600">
              <h3 className="text-sm text-gray-300 mb-2">Verified Reunions</h3>
              <p className="text-3xl font-bold">0</p>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-primary/50 border-gray-600">
              <h3 className="text-lg font-semibold mb-4">Live Timeline</h3>
              <p className="text-gray-300">No active missions</p>
            </Card>

            <Card className="bg-primary/50 border-gray-600">
              <h3 className="text-lg font-semibold mb-4">Statistics</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-300">Average Response Time</span>
                  <span className="font-medium">0 min</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Success Rate</span>
                  <span className="font-medium">0%</span>
                </div>
              </div>
            </Card>
          </div>

          <Card className="mt-6 bg-primary/50 border-gray-600">
            <h3 className="text-lg font-semibold mb-4">Incident Map</h3>
            <div className="h-64 bg-gray-800 rounded-lg flex items-center justify-center">
              <p className="text-gray-400">Map placeholder</p>
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}