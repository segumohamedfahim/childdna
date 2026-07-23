import { Routes, Route, Navigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import MissionInit from './pages/MissionInit'
import Landing from './pages/Landing'
import GuardianDashboard from './pages/GuardianDashboard'
import FirstHelperConsole from './pages/FirstHelperConsole'
import AuthorityDashboard from './pages/AuthorityDashboard'
import MissionControl from './pages/MissionControl'
import MissionComplete from './pages/MissionComplete'
import Navbar from './components/layout/Navbar'

function App() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<MissionInit />} />
          <Route path="/landing" element={<Landing />} />
          <Route path="/guardian" element={<GuardianDashboard />} />
          <Route path="/helper" element={<FirstHelperConsole />} />
          <Route path="/authority" element={<AuthorityDashboard />} />
          <Route path="/control" element={<MissionControl />} />
          <Route path="/complete" element={<MissionComplete />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AnimatePresence>
    </div>
  )
}

export default App