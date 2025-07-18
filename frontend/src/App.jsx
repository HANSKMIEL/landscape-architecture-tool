import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'sonner'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './components/Dashboard'
import Suppliers from './components/Suppliers'
import Plants from './components/Plants'
import Products from './components/Products'
import Clients from './components/Clients'
import Projects from './components/Projects'
import PlantRecommendations from './components/PlantRecommendations'
import Reports from './components/Reports'
import Settings from './components/Settings'
import './App.css'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [language, setLanguage] = useState('en')

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen)
  const toggleLanguage = () => setLanguage(language === 'en' ? 'nl' : 'en')

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        <div className={`transition-all duration-300 ${sidebarOpen ? 'lg:ml-64' : 'lg:ml-64'}`}>
          <Header 
            onMenuClick={toggleSidebar}
            language={language}
            onLanguageToggle={toggleLanguage}
          />
          
          <main className="p-6">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard language={language} />} />
              <Route path="/suppliers" element={<Suppliers language={language} />} />
              <Route path="/products" element={<Products language={language} />} />
              <Route path="/plants" element={<Plants language={language} />} />
              <Route path="/clients" element={<Clients language={language} />} />
              <Route path="/projects" element={<Projects language={language} />} />
              <Route path="/plant-recommendations" element={<PlantRecommendations language={language} />} />
              <Route path="/reports" element={<Reports language={language} />} />
              <Route path="/settings" element={<Settings language={language} />} />
            </Routes>
          </main>
        </div>
        
        <Toaster position="top-right" />
      </div>
    </Router>
  )
}

export default App

