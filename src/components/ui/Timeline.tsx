import { motion } from 'framer-motion'

const timelineSteps = [
  { id: 1, label: 'Token Activated' },
  { id: 2, label: 'Guardian Notified' },
  { id: 3, label: 'REUNITE AI' },
  { id: 4, label: 'Verified Reunion' },
]

export function Timeline() {
  return (
    <div className="max-w-md mx-auto">
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-300" />
        
        {timelineSteps.map((step, index) => (
          <motion.div
            key={step.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.2, duration: 0.5 }}
            className="relative flex items-center mb-8 last:mb-0"
          >
            {/* Circle indicator */}
            <div className="absolute left-0 w-10 h-10 bg-accent rounded-full flex items-center justify-center text-white font-bold z-10">
              {step.id}
            </div>
            
            {/* Content */}
            <div className="ml-16">
              <p className="text-primary font-medium">{step.label}</p>
            </div>
            
            {/* Arrow */}
            {index < timelineSteps.length - 1 && (
              <div className="absolute left-4 -bottom-4 text-gray-400">
                ↓
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  )
}