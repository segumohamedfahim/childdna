import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

const missionSteps = [
  'Mission Initializing...',
  'Checking Identity...',
  'Preparing Rescue Session...',
  'Connecting Guardian...',
  'Ready.',
]

export default function MissionInit() {
  const navigate = useNavigate()

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/landing')
    }, 4000)
    return () => clearTimeout(timer)
  }, [navigate])

  return (
    <div className="flex min-h-screen items-center justify-center bg-primary">
      <div className="text-center">
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="mb-8 text-6xl"
        >
          🧬
        </motion.div>
        
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="mb-2 text-3xl font-bold text-white"
        >
          Child DNA
        </motion.h1>
        
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="mb-12 text-lg text-gray-300"
        >
          Powered by REUNITE AI
        </motion.p>

        <div className="space-y-4">
          <AnimatePresence>
            {missionSteps.map((step, index) => (
              <motion.p
                key={step}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.8, duration: 0.5 }}
                className="text-accent text-lg"
              >
                {step}
              </motion.p>
            ))}
          </AnimatePresence>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.5 }}
          className="mt-12"
        >
          <div className="h-1 w-48 mx-auto bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-accent"
              initial={{ width: 0 }}
              animate={{ width: '100%' }}
              transition={{ duration: 4, ease: 'easeInOut' }}
            />
          </div>
        </motion.div>
      </div>
    </div>
  )
}