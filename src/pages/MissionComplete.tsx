import { motion } from 'framer-motion'
import { CheckCircle2 } from 'lucide-react'
import { StatusBadge } from '@/components/ui/StatusBadge'

export default function MissionComplete() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-primary">
      <div className="text-center max-w-md">
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, type: 'spring' }}
          className="mb-8"
        >
          <CheckCircle2 className="w-20 h-20 text-success mx-auto" />
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="text-4xl font-bold text-white mb-6"
        >
          MISSION COMPLETE
        </motion.h1>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="space-y-4 mb-8"
        >
          <p className="text-xl text-gray-300">Child Safe</p>
          <p className="text-xl text-gray-300">Guardian Verified</p>
          <p className="text-xl text-gray-300">Privacy Protected</p>
          <p className="text-xl text-gray-300">Average Rescue Time: 0 min</p>
        </motion.div>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7, duration: 0.5 }}
          className="text-lg text-gray-400 mb-8"
        >
          Because someone chose to help.
        </motion.p>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9, duration: 0.5 }}
        >
          <StatusBadge status="complete" />
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.1, duration: 0.5 }}
          className="mt-8 text-gray-400"
        >
          Powered by REUNITE AI
        </motion.p>
      </div>
    </div>
  )
}