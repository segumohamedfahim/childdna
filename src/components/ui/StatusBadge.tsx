import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface StatusBadgeProps {
  status: 'online' | 'active' | 'complete'
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const statusConfig = {
    online: { color: 'bg-success', text: 'SYSTEM ONLINE', dot: '🟢' },
    active: { color: 'bg-warning', text: 'MISSION ACTIVE', dot: '🟡' },
    complete: { color: 'bg-success', text: 'MISSION COMPLETE', dot: '🟢' },
  }

  const config = statusConfig[status]

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn(
        'inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium text-white',
        config.color,
        className
      )}
    >
      <span>{config.dot}</span>
      <span>{config.text}</span>
    </motion.div>
  )
}