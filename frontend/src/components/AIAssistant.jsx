import React, { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input as _Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Bot, 
  Send, 
  Loader2, 
  Lightbulb, 
  Leaf, 
  TrendingUp, 
  MessageSquare,
  Sparkles,
  Brain,
  Target,
  BarChart3,
  FileText,
  Zap,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react'
import { useLanguage } from '../i18n/LanguageProvider'
import ApiService from '../services/api'

const AIAssistant = () => {
  const { t, language } = useLanguage()
  const [activeTab, setActiveTab] = useState('chat')
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [_suggestions, _setSuggestions] = useState([])
  const [insights, setInsights] = useState([])
  const [plantRecommendations, setPlantRecommendations] = useState([])
  const messagesEndRef = useRef(null)

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize with welcome message
  useEffect(() => {
    const welcomeMessage = {
      id: Date.now(),
      type: 'assistant',
      content: language === 'nl' 
        ? 'Hallo! Ik ben je AI-assistent voor landschapsarchitectuur. Ik kan je helpen met plantaanbevelingen, projectinzichten, en data-analyse. Hoe kan ik je vandaag helpen?'
        : 'Hello! I\'m your landscape architecture AI assistant. I can help you with plant recommendations, project insights, and data analysis. How can I help you today?',
      timestamp: new Date()
    }
    setMessages([welcomeMessage])
    loadInitialData, [loadInitialData]()
  }, [language])

  // Load initial data for insights
  const loadInitialData, [loadInitialData] = async () => {
    try {
      // Generate initial insights
      await generateInsights()
      await generatePlantRecommendations()
    } catch (error) {
      console.error('Error loading initial data:', error)
    }
  }

  // Send message to AI
  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Call AI API
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          language: language,
          context: 'landscape_architecture'
        })
      })

      if (!response.ok) {
        throw new Error('AI service unavailable')
      }

      const data = await response.json()
      
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.response || 'I apologize, but I couldn\'t process your request at the moment.',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])

    } catch (error) {
      console.error('AI chat error:', error)
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: language === 'nl' 
          ? 'Sorry, ik kan je vraag momenteel niet verwerken. Probeer het later opnieuw.'
          : 'Sorry, I can\'t process your question right now. Please try again later.',
        timestamp: new Date(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // Generate business insights
  const generateInsights = async () => {
    try {
      // Get dashboard stats for context
      const stats = await ApiService.getDashboardStats()
      
      const insightPrompts = [
        {
          type: 'performance',
          icon: TrendingUp,
          title: language === 'nl' ? 'Prestatie Analyse' : 'Performance Analysis',
          prompt: `Based on ${stats.total_projects} projects and ${stats.total_clients} clients, what are key performance insights?`
        },
        {
          type: 'growth',
          icon: BarChart3,
          title: language === 'nl' ? 'Groei Mogelijkheden' : 'Growth Opportunities',
          prompt: `With current project portfolio, what growth opportunities exist?`
        },
        {
          type: 'efficiency',
          icon: Zap,
          title: language === 'nl' ? 'Efficiëntie Tips' : 'Efficiency Tips',
          prompt: `How can landscape architecture workflow be optimized?`
        }
      ]

      const generatedInsights = insightPrompts.map(insight => ({
        ...insight,
        content: language === 'nl' 
          ? `Gebaseerd op je huidige data van ${stats.total_projects} projecten en ${stats.total_clients} klanten, raad ik aan om te focussen op het verbeteren van client retentie en het uitbreiden van je plantencatalogus.`
          : `Based on your current data of ${stats.total_projects} projects and ${stats.total_clients} clients, I recommend focusing on improving client retention and expanding your plant catalog.`,
        id: Date.now() + Math.random()
      }))

      setInsights(generatedInsights)

    } catch (error) {
      console.error('Error generating insights:', error)
    }
  }

  // Generate plant recommendations
  const generatePlantRecommendations = async () => {
    try {
      const plants = await ApiService.getPlants()
      
      const recommendations = [
        {
          id: 1,
          type: 'native',
          title: language === 'nl' ? 'Inheemse Planten' : 'Native Plants',
          description: language === 'nl' 
            ? 'Bevorder biodiversiteit met inheemse plantensoorten'
            : 'Promote biodiversity with native plant species',
          plants: plants.plants?.filter(p => p.native).slice(0, 3) || [],
          icon: Leaf,
          color: 'text-green-600'
        },
        {
          id: 2,
          type: 'drought_resistant',
          title: language === 'nl' ? 'Droogtebestendige Planten' : 'Drought Resistant Plants',
          description: language === 'nl' 
            ? 'Waterbesparende opties voor duurzame tuinen'
            : 'Water-saving options for sustainable gardens',
          plants: plants.plants?.filter(p => p.water_needs === 'low').slice(0, 3) || [],
          icon: Target,
          color: 'text-blue-600'
        },
        {
          id: 3,
          type: 'seasonal',
          title: language === 'nl' ? 'Seizoensgebonden Keuzes' : 'Seasonal Choices',
          description: language === 'nl' 
            ? 'Perfecte planten voor het huidige seizoen'
            : 'Perfect plants for the current season',
          plants: plants.plants?.slice(0, 3) || [],
          icon: Sparkles,
          color: 'text-purple-600'
        }
      ]

      setPlantRecommendations(recommendations)

    } catch (error) {
      console.error('Error generating plant recommendations:', error)
    }
  }

  // Quick suggestion buttons
  const quickSuggestions = [
    {
      text: language === 'nl' ? 'Plantaanbevelingen voor schaduwrijke plekken' : 'Plant recommendations for shady areas',
      icon: Leaf
    },
    {
      text: language === 'nl' ? 'Hoe kan ik mijn projecten beter organiseren?' : 'How can I better organize my projects?',
      icon: FileText
    },
    {
      text: language === 'nl' ? 'Wat zijn de trends in landschapsarchitectuur?' : 'What are the trends in landscape architecture?',
      icon: TrendingUp
    },
    {
      text: language === 'nl' ? 'Tips voor duurzaam tuinontwerp' : 'Tips for sustainable garden design',
      icon: Target
    }
  ]

  const handleQuickSuggestion = (suggestion) => {
    setInputMessage(suggestion.text)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Bot className="h-8 w-8 mr-3 text-green-600" />
            {t('aiAssistant.title', 'AI Assistant')}
          </h1>
          <p className="text-gray-600">
            {t('aiAssistant.subtitle', 'Get intelligent insights and recommendations for your landscape projects')}
          </p>
        </div>
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="chat" className="flex items-center space-x-2">
            <MessageSquare className="h-4 w-4" />
            <span>{t('aiAssistant.chat', 'Chat')}</span>
          </TabsTrigger>
          <TabsTrigger value="insights" className="flex items-center space-x-2">
            <Brain className="h-4 w-4" />
            <span>{t('aiAssistant.insights', 'Insights')}</span>
          </TabsTrigger>
          <TabsTrigger value="recommendations" className="flex items-center space-x-2">
            <Lightbulb className="h-4 w-4" />
            <span>{t('aiAssistant.recommendations', 'Recommendations')}</span>
          </TabsTrigger>
        </TabsList>

        {/* Chat Tab */}
        <TabsContent value="chat" className="space-y-4">
          <Card className="h-96">
            <CardContent className="p-0 h-full flex flex-col">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] p-3 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-green-600 text-white'
                          : message.isError
                          ? 'bg-red-50 text-red-800 border border-red-200'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      <div className="flex items-start space-x-2">
                        {message.type === 'assistant' && (
                          <Bot className={`h-4 w-4 mt-0.5 ${message.isError ? 'text-red-600' : 'text-green-600'}`} />
                        )}
                        <div className="flex-1">
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                          <p className="text-xs opacity-70 mt-1">
                            {message.timestamp.toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 p-3 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <Bot className="h-4 w-4 text-green-600" />
                        <Loader2 className="h-4 w-4 animate-spin text-gray-600" />
                        <span className="text-sm text-gray-600">
                          {t('aiAssistant.thinking', 'Thinking...')}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="border-t p-4">
                <div className="flex space-x-2">
                  <Textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={t('aiAssistant.messagePlaceholder', 'Ask me anything about landscape architecture...')}
                    className="flex-1 min-h-[40px] max-h-[120px] resize-none"
                    rows={1}
                  />
                  <Button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    className="px-3"
                  >
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                </div>

                {/* Quick Suggestions */}
                <div className="mt-3 flex flex-wrap gap-2">
                  {quickSuggestions.map((suggestion, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      onClick={() => handleQuickSuggestion(suggestion)}
                      className="text-xs"
                    >
                      <suggestion.icon className="h-3 w-3 mr-1" />
                      {suggestion.text}
                    </Button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Insights Tab */}
        <TabsContent value="insights" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {insights.map((insight) => (
              <Card key={insight.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center text-sm">
                    <insight.icon className="h-4 w-4 mr-2 text-green-600" />
                    {insight.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">{insight.content}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="h-5 w-5 mr-2" />
                {t('aiAssistant.dataAnalysis', 'Data Analysis')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Info className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-800">
                      {t('aiAssistant.projectTrend', 'Project Trend Analysis')}
                    </span>
                  </div>
                  <Badge variant="secondary">
                    {t('aiAssistant.positive', 'Positive')}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-green-800">
                      {t('aiAssistant.clientSatisfaction', 'Client Satisfaction')}
                    </span>
                  </div>
                  <Badge variant="secondary">
                    {t('aiAssistant.excellent', 'Excellent')}
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="h-4 w-4 text-yellow-600" />
                    <span className="text-sm font-medium text-yellow-800">
                      {t('aiAssistant.resourceUtilization', 'Resource Utilization')}
                    </span>
                  </div>
                  <Badge variant="secondary">
                    {t('aiAssistant.needsAttention', 'Needs Attention')}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Recommendations Tab */}
        <TabsContent value="recommendations" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {plantRecommendations.map((recommendation) => (
              <Card key={recommendation.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center text-sm">
                    <recommendation.icon className={`h-4 w-4 mr-2 ${recommendation.color}`} />
                    {recommendation.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-3">{recommendation.description}</p>
                  <div className="space-y-2">
                    {recommendation.plants.map((plant, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm font-medium">{plant.name}</span>
                        {plant.native && (
                          <Badge variant="outline" className="text-xs">
                            {t('plants.native', 'Native')}
                          </Badge>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="h-5 w-5 mr-2" />
                {t('aiAssistant.actionableRecommendations', 'Actionable Recommendations')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-start space-x-3 p-3 border border-green-200 rounded-lg bg-green-50">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-green-800">
                      {t('aiAssistant.expandNativePlants', 'Expand Native Plant Collection')}
                    </h4>
                    <p className="text-sm text-green-700">
                      {t('aiAssistant.expandNativePlantsDesc', 'Add more native species to promote local biodiversity and reduce maintenance costs.')}
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-3 border border-blue-200 rounded-lg bg-blue-50">
                  <Info className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-blue-800">
                      {t('aiAssistant.improveDataCollection', 'Improve Data Collection')}
                    </h4>
                    <p className="text-sm text-blue-700">
                      {t('aiAssistant.improveDataCollectionDesc', 'Implement systematic data collection for better project insights and client reporting.')}
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-3 border border-purple-200 rounded-lg bg-purple-50">
                  <Sparkles className="h-5 w-5 text-purple-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-purple-800">
                      {t('aiAssistant.seasonalPlanning', 'Seasonal Planning Strategy')}
                    </h4>
                    <p className="text-sm text-purple-700">
                      {t('aiAssistant.seasonalPlanningDesc', 'Develop seasonal planting schedules to optimize growth and visual impact throughout the year.')}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default AIAssistant
