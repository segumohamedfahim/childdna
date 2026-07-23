import { motion } from 'framer-motion'
import { StatCard } from '@/components/ui/StatCard'
import { StatusBadge } from '@/components/ui/StatusBadge'

export default function MissionControl() {
  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="container mx-auto max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-primary">Mission Control</h1>
            <StatusBadge status="online" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Children Registered"
              value={0}
              delay={0}
            />
            <StatCard
              title="Rescue Sessions"
              value={0}
              delay={0.1}
            />
            <StatCard
              title="Verified Reunions"
              value={0}
              delay={0.2}
            />
            <StatCard
              title="Average Rescue Time"
              value="0 min"
              delay={0.3}
            />
          </div>
        </motion.div>
      </div>
    </div>
  )
}