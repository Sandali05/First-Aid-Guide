import React, { useEffect, useMemo, useState } from 'react'
import { continueChat, ChatMessage } from './api'

const styles = `
:root {
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

body {
  margin: 0;
}

.chat-app {
  min-height: 100vh;
  background-color: #f5f6fb;
  background-image: url('https://i.pinimg.com/originals/4c/98/4e/4c984ef0291409fef0a0942b391f6287.jpg');
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center;
  background-attachment: fixed;
  color: #1f1f3d;
  padding: 32px;
  box-sizing: border-box;
  position: relative;
  isolation: isolate;
}

.chat-app::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(245, 246, 251, 0.88);
  z-index: -1;
}

.chat-shell {
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: relative;
  z-index: 1;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-radius: 24px;
  background: #ffffff;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.08);
}

.chat-header h1 {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 6px;
}

.chat-header p {
  margin: 0;
  color: #6b6b80;
  font-size: 15px;
}

.chat-header .header-actions {
  display: flex;
  gap: 8px;
}

.chat-header .pill-button {
  border: none;
  background: #f6f7fb;
  color: #1f1f3d;
  padding: 10px 16px;
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
}

.chat-header .pill-button.primary {
  background: #ff4d67;
  color: #fff;
}

.chat-layout {
  display: flex;
  align-items: flex-start;
  gap: 28px;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
  order: 2;
  max-width: 320px;
  width: 100%;
  margin-left: auto;
  position: sticky;
  top: 0;
}

.sidebar-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.07);
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.sidebar-card h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}

.sidebar-card p {
  margin: 0;
  color: #6b6b80;
  font-size: 14px;
  line-height: 1.5;
}

.map-container {
  position: relative;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.12);
  height: 200px;
}

.map-container iframe {
  border: 0;
  width: 100%;
  height: 100%;
}

.map-container a {
  position: absolute;
  inset: 0;
  text-indent: -9999px;
}

.map-button {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: #1f70ff;
  color: #fff;
  border-radius: 12px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.2s ease-in-out;
}

.map-button:hover {
  background: #1558d6;
}

.video-grid {
  display: grid;
  gap: 14px;
}

.video-card {
  display: grid;
  grid-template-columns: 96px 1fr;
  gap: 12px;
  padding: 12px;
  border-radius: 16px;
  background: #f6f7fb;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.video-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 24px rgba(15, 23, 42, 0.12);
}

.video-card img {
  width: 100%;
  height: 100%;
  border-radius: 12px;
  object-fit: cover;
}

.video-card h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}

.video-card span {
  font-size: 13px;
  color: #6b6b80;
}

.main-panel {
  display: flex;
  flex: 1 1 auto;
  min-width: 0;
  flex-direction: column;
  gap: 18px;
  order: 1;
}

.conversation-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.07);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.conversation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #42c78b;
  margin-right: 8px;
}

.status-text {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #42c78b;
  font-weight: 600;
}

.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.quick-button {
  border: none;
  padding: 8px 16px;
  border-radius: 999px;
  background: rgba(222, 222, 225, 0.12);
  color: #464678ff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.quick-button:hover {
  background: rgba(89, 92, 255, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(89, 92, 255, 0.18);
}

.quick-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 4px 6px;
  max-height: 440px;
  overflow-y: auto;
}

.message {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 72%;
}

.message.assistant {
  align-self: flex-start;
  text-align: left;
}

.message.user {
  align-self: flex-end;
  text-align: right;
}

.message-content {
  padding: 16px 20px;
  border-radius: 22px;
  line-height: 1.6;
  white-space: pre-wrap;
  font-size: 15px;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.08);
}

.message.assistant .message-content {
  background: #f5f1ff;
  border: 1px solid #e5dcff;
  border-top-left-radius: 8px;
}

.message.user .message-content {
  background: #ffe9f1;
  border: 1px solid #ffd0df;
  border-top-right-radius: 8px;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #8c8ca6;
  letter-spacing: 0.01em;
}

.message.assistant .message-meta {
  justify-content: flex-start;
}

.message.user .message-meta {
  justify-content: flex-end;
}

.message-author {
  font-weight: 600;
  color: #4a4a6a;
}

.input-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 20px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.07);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

textarea.chat-input {
  width: 100%;
  min-height: 96px;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid #d9dcec;
  font-size: 15px;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
  display: block;
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.action-row .hint {
  color: #6b6b80;
  font-size: 13px;
}

.send-button {
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  background: linear-gradient(120deg, #595cff, #ff6584);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.send-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-banner {
  background: #ffe5e8;
  color: #d8405f;
  border-radius: 16px;
  padding: 14px 18px;
  font-weight: 600;
}

@media (max-width: 960px) {
  .chat-shell::before,
  .chat-shell::after {
    display: none;
  }

  .chat-layout {
    flex-direction: column;
    gap: 20px;
  }

  .sidebar {
    order: 2;
    position: static;
    max-width: none;
    width: 100%;
    margin-left: 0;
  }

  .main-panel {
    order: 1;
  }
}
`

type QuickVideo = {
  id: string
  title: string
  description: string
  url: string
  imageUrl: string
}

type DisplayMessage = ChatMessage & {
  id: string
  timestamp: Date
}

const mapSearchUrl = 'https://www.google.com/maps/search/nearest+hospitals%2Fmedi+help/'

const generateId = () => Math.random().toString(36).slice(2, 10)

const sanitizeContent = (content: string) => content.replace(/\*\*/g, '')

const createDisplayMessage = (message: ChatMessage, timestamp?: Date): DisplayMessage => ({
  ...message,
  id: `${message.role}-${generateId()}`,
  timestamp: timestamp ?? new Date()
})

const reconcileMessages = (
  existing: DisplayMessage[],
  incoming: ChatMessage[]
): DisplayMessage[] => {
  const pool = [...existing]

  return incoming.map(message => {
    const matchIndex = pool.findIndex(
      candidate => candidate.role === message.role && candidate.content === message.content
    )

    if (matchIndex >= 0) {
      const [match] = pool.splice(matchIndex, 1)
      return match
    }

    return createDisplayMessage(message)
  })
}

const formatTimestamp = (value: Date) =>
  value.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  })

export default function App() {
  useEffect(() => {
    const styleTag = document.createElement('style')
    styleTag.setAttribute('data-first-aid-styles', 'true')
    styleTag.textContent = styles
    document.head.appendChild(styleTag)
    return () => {
      document.head.removeChild(styleTag)
    }
  }, [])

  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<DisplayMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const quickVideos: QuickVideo[] = useMemo(
    () => [
      {
        id: 'severe-bleeding',
        title: 'Severe bleeding',
        description: 'Stop bleeding fast with direct pressure and elevation.',
        url: 'https://youtu.be/p9KHec6xfuw?si=5CFsfHX1Kb4-cPBg',
        imageUrl:
          'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSbbzL1xbwqtpvxFrE0tfOEpkujg_QFphzY3A&s'
      },
      {
        id: 'cpr-basics',
        title: 'CPR basics',
        description: 'Hands-only CPR technique for adults and teens.',
        url: 'https://youtu.be/TsJ49Np3HS0?si=nGaGMFFmP2XEtcpu',
        imageUrl: 'https://skillstrainingcollege.com.au/wp-content/uploads/2022/12/Blog-CPR-960-%C3%97-540px.png'
      },
      {
        id: 'burn-treatment',
        title: 'Burn treatment',
        description: 'Cool the burn and cover it safely until help arrives.',
        url: 'https://youtu.be/v2mY1h0BdTw?si=rZAVjQr2GyP1xi1t',
        imageUrl: 'https://hurak.com/blog/wp-content/uploads/2025/01/first-aid-tips-for-burn.webp'
      }
    ],
    []
  )

  const quickPrompts = useMemo(
    () => ['CPR steps', 'Stopping bleeding', 'Burn care', 'Sprain support'],
    []
  )

  const defaultConversation = useMemo(
    () => [
      createDisplayMessage(
        {
          role: 'assistant',
          content: "I'm your First-Aid Guide. Who needs help and where are you?"
        },
        new Date('2024-04-10T09:12:00')
      ),
      createDisplayMessage(
        {
          role: 'user',
          content: "Adult with a cut on the forearm. We're at the park."
        },
        new Date('2024-04-10T09:18:00')
      ),
      createDisplayMessage(
        {
          role: 'assistant',
          content:
            "Apply direct pressure with clean cloth for 5–10 minutes. Elevate the arm if possible. I'll show nearby clinics on the map."
        },
        new Date('2024-04-10T09:19:00')
      ),
      createDisplayMessage(
        {
          role: 'user',
          content: 'CPR steps'
        },
        new Date('2024-04-10T09:39:00')
      )
    ],
    []
  )

  const onSend = async () => {
    const trimmed = input.trim()
    if (!trimmed) return

    setLoading(true)
    setError(null)

    const userChatMessage: ChatMessage = { role: 'user', content: trimmed }
    const history = [
      ...messages.map(({ role, content }) => ({ role, content })),
      userChatMessage
    ]
    const userDisplayMessage = createDisplayMessage(userChatMessage)

    setMessages(prev => [...prev, userDisplayMessage])

    try {
      const data = await continueChat(history)
      setMessages(prev => reconcileMessages(prev, data.messages))
      setInput('')
    } catch (err) {
      setError('Failed to get a response from the assistant. Please try again.')
      setMessages(prev => prev.filter(message => message.id !== userDisplayMessage.id))
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const onQuickPrompt = (prompt: string) => {
    if (loading) return
    setInput(prompt)
  }

  const activeMessages = messages.length === 0 ? defaultConversation : messages

  return (
    <div className="chat-app">
      <div className="chat-shell">
        <header className="chat-header">
          <div>
            <h1>First-Aid Guide</h1>
            <p>Calm, step-by-step help. Not a substitute for professional care.</p>
          </div>
          <div className="header-actions">
            <button className="pill-button">Emergency</button>
            <button className="pill-button primary">Stop</button>
          </div>
        </header>

        <div className="chat-layout">
          <aside className="sidebar">
            <section className="sidebar-card">
              <h2>Nearby Help</h2>
              <p>Find urgent care centers and hospitals close to you.</p>
              <div className="map-container">
                <iframe
                  title="Nearby hospitals map"
                  src="https://www.google.com/maps?q=nearest%20hospitals%2Fmedi%20help&output=embed"
                  allowFullScreen
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                />
                <a href={mapSearchUrl} target="_blank" rel="noopener noreferrer">
                  Open in Google Maps
                </a>
              </div>
              <a className="map-button" href={mapSearchUrl} target="_blank" rel="noopener noreferrer">
                Open in Google Maps
              </a>
            </section>

            <section className="sidebar-card">
              <h2>Quick Reference</h2>
              <p>Watch essential first-aid refreshers while help is on the way.</p>
              <div className="video-grid">
                {quickVideos.map(video => (
                  <a
                    key={video.id}
                    className="video-card"
                    href={video.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <img
                      src={video.imageUrl}
                      alt={`${video.title} thumbnail`}
                      loading="lazy"
                    />
                    <div>
                      <h3>{video.title}</h3>
                      <span>{video.description}</span>
                    </div>
                  </a>
                ))}
              </div>
            </section>
          </aside>

          <main className="main-panel">
            <section className="conversation-card">
              <div className="conversation-header">
                <div>
                  <div className="status-text">
                    <span className="status-dot" />
                    Live assistant
                  </div>
                  <p style={{ color: '#6b6b80', margin: '6px 0 0', fontSize: 14 }}>
                    Conversation
                  </p>
                </div>
                <div className="quick-actions">
                  {quickPrompts.map(prompt => (
                    <button
                      key={prompt}
                      type="button"
                      className="quick-button"
                      onClick={() => onQuickPrompt(prompt)}
                      disabled={loading}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>

              <div className="messages">
                {activeMessages.map(message => (
                  <div key={message.id} className={`message ${message.role}`}>
                    <div className="message-content">{sanitizeContent(message.content)}</div>
                    <div className="message-meta">
                      <span className="message-author">
                        {message.role === 'assistant'
                          ? 'Assistant'
                          : message.role === 'user'
                          ? 'You'
                          : 'System'}
                      </span>
                      <span>{formatTimestamp(message.timestamp)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="input-card">
              <textarea
                className="chat-input"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Describe the situation (e.g., adult with a cut on the forearm)."
              />
              <div className="action-row">
                <span className="hint">The assistant will answer with calm, clear steps.</span>
                <button className="send-button" onClick={onSend} disabled={loading}>
                  {loading ? 'Thinking…' : 'Send'}
                </button>
              </div>
              {error && <div className="error-banner">{error}</div>}
            </section>
          </main>
        </div>
      </div>
    </div>
  )
}
