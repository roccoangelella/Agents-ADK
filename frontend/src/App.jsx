import { useState } from 'react'
import './App.css'

function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('unknown')

  const checkConnection = async () => {
    setConnectionStatus('checking')
    try {
      const response = await fetch('http://localhost:8081/health', {
        method: 'GET',
      })
      if (response.ok) {
        setConnectionStatus('connected')
      } else {
        setConnectionStatus('error')
      }
    } catch (error) {
      setConnectionStatus('error')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    // Add user message to chat
    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Replace with your actual API endpoint
      const response = await fetch('http://localhost:8081/mcp/prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          inputs: {
            text: input
          }
        }),
      })

      const data = await response.json()
      
      // Add agent response to chat
      setMessages(prev => [...prev, { role: 'agent', content: data.outputs.text }])
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, { role: 'error', content: 'Sorry, something went wrong.' }])
    }

    setIsLoading(false)
  }

  return (
    <div className="app-container">
      <header>
        <h1>AI Agent Chat</h1>
        <div className="connection-status">
          <button 
            onClick={checkConnection}
            disabled={connectionStatus === 'checking'}
            className={`status-button ${connectionStatus}`}
          >
            {connectionStatus === 'checking' ? 'Checking...' : 'Check Connection'}
          </button>
          {connectionStatus !== 'unknown' && (
            <span className={`status-indicator ${connectionStatus}`}>
              {connectionStatus === 'connected' ? '✓ Connected' : 
               connectionStatus === 'error' ? '✕ Not Connected' : 
               '⋯ Checking'}
            </span>
          )}
        </div>
      </header>
      
      <div className="chat-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-content">{message.content}</div>
          </div>
        ))}
        {isLoading && (
          <div className="message agent">
            <div className="message-content">Thinking...</div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          Send
        </button>
      </form>
    </div>
  )
}

export default App
