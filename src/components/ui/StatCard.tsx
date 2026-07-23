import { motion, useMotionValue, useTransform, animate } from 'framer-motion'
import { useEffect } from 'react'
import { Card } from './Card'

interface StatCardProps {
  title: string
  value: number | string
  delay?: number
}

export function StatCard({ title, value, delay = 0 }: StatCardProps) {
  const count = useMotionValue(0)
  const rounded = useTransform(count, Math.round)

  useEffect(() => {
    const controls = animate(count, typeof value === 'number' ? value : 0, {
      duration: 2,
      delay,
      ease: 'easeOut',
    })
    return () => controls.stop()
  }, [count, value, delay])

  return (
    <Card>
      <h3 className="text-sm text-gray-500 mb-2">{title}</h3>
      <motion.p
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: delay + 0.3, duration: 0.5 }}
        className="text-3xl font-bold text-primary"
      >
        {typeof value === 'number' ? rounded : value}
      </motion.p>
    </Card>
  )
}