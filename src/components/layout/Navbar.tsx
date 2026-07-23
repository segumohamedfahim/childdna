import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { StatusBadge } from '@/components/ui/StatusBadge'

const navItems = [
  { name: 'Home', path: '/landing' },
  { name: 'Guardian', path: '/guardian' },
  { name: 'First Helper', path: '/helper' },
  { name: 'Authority', path: '/authority' },
  { name: 'Mission Control', path: '/control' },
]

export default function Navbar() {
  const location = useLocation()

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/80 backdrop-blur-sm">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link to="/landing" className="flex items-center space-x-2">
          <span className="text-2xl font-bold text-primary">Child DNA</span>
        </Link>
        
        <nav className="hidden md:flex items-center space-x-6">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'text-sm font-medium transition-colors hover:text-accent',
                location.pathname === item.path ? 'text-accent' : 'text-primary'
              )}
            >
              {item.name}
            </Link>
          ))}
        </nav>

        <div className="flex items-center">
          <StatusBadge status="online" />
        </div>
      </div>
    </header>
  )
}
