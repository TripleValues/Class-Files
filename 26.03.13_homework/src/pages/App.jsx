import { useState, useRef, useEffect } from 'react'
import '@styles/App3.css'

const N8N_WEBHOOK_URL = import.meta.env.VITE_N8N_WEBHOOK_URL || '/webhook/your-webhook-id'

function TypingDots() {
  return (
    <div className="message">
      <div className="message__avatar">G</div>
      <div className="message__bubble message__bubble--assistant">
        <div className="typing-dots">
          <span /><span /><span />
        </div>
      </div>
    </div>
  )
}

function Message({ role, content }) {
  const isUser = role === 'user'
  return (
    <div className={`message ${isUser ? 'message--user' : ''}`}>
      {!isUser && <div className="message__avatar">G</div>}
      <div className={`message__bubble ${isUser ? 'message__bubble--user' : 'message__bubble--assistant'}`}>
        {content}
      </div>
      {isUser && <div className="message__avatar message__avatar--user">👤</div>}
    </div>
  )
}

export default function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '안녕하세요! 무엇이든 물어보세요 ✨' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function sendMessage() {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    setError('')

    const newMessages = [...messages, { role: 'user', content: text }]
    setMessages(newMessages)
    setLoading(true)

    try {
      const res = await fetch(N8N_WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: newMessages.map(({ role, content }) => ({ role, content }))
        })
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const data = await res.json()

      // n8n 응답 형식에 맞게 수정하세요
      const reply = data.output || data.message || data.text || '응답을 받았습니다.'

      setMessages(prev => [...prev, { role: 'assistant', content: reply }])
    } catch (e) {
      setError('n8n 서버에 연결할 수 없습니다. Webhook URL을 확인해주세요.')
    } finally {
      setLoading(false)
      textareaRef.current?.focus()
    }
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  function handleInput(e) {
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
  }

  function clearChat() {
    setMessages([{ role: 'assistant', content: '대화가 초기화되었습니다 ✨' }])
    setError('')
  }

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header__info">
          <div className="chat-header__avatar">G</div>
          <div>
            <div className="chat-header__name">Gemma 3.4b</div>
            <div className="chat-header__status">
              <span className="status-dot" />
              n8n · Ollama
            </div>
          </div>
        </div>
        <button className="chat-header__clear" onClick={clearChat}>초기화</button>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <Message key={i} role={msg.role} content={msg.content} />
        ))}
        {loading && <TypingDots />}
        {error && <div className="chat-error">⚠️ {error}</div>}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="chat-input">
        <div className="chat-input__box">
          <textarea
            ref={textareaRef}
            className="chat-input__textarea"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            onInput={handleInput}
            placeholder="메시지를 입력하세요... (Enter로 전송)"
            rows={1}
          />
          <button
            className="chat-input__send"
            onClick={sendMessage}
            disabled={!input.trim() || loading}
          >
            ↑
          </button>
        </div>
        <div className="chat-input__hint">shift+enter 줄바꿈 · n8n webhook</div>
      </div>
    </div>
  )
}