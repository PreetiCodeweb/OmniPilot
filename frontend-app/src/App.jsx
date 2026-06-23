import { useEffect, useRef, useState } from 'react';
import { useChat } from './hooks/useChat';
import Sidebar from './components/Sidebar';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import QuickPrompts from './components/QuickPrompts';

export default function App() {
  const { messages, isLoading, taskRunning, send } = useChat();
  const bottomRef = useRef(null);
  const [showPrompts, setShowPrompts] = useState(true);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (text) => {
    setShowPrompts(false);
    send(text);
  };

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar taskRunning={taskRunning} />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--bg)' }}>
        {/* Header */}
        <div style={{
          padding: '16px 24px',
          borderBottom: '1px solid var(--border)',
          background: 'var(--bg-surface)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexShrink: 0,
        }}>
          <div>
            <h1 style={{ fontSize: '16px', fontWeight: 700, letterSpacing: '-0.02em' }}>Social AI Agent</h1>
            <p style={{ fontSize: '12px', color: 'var(--text-3)' }}>Browser automation for Twitter · LinkedIn · Reddit · WhatsApp</p>
          </div>
          <div style={{ display: 'flex', gap: '6px' }}>
            {['🤖 Browser Use', 'n8n ready', 'Claude AI'].map(tag => (
              <span key={tag} style={{
                fontSize: '10px', background: 'var(--bg-card)', border: '1px solid var(--border)',
                borderRadius: '20px', padding: '3px 9px', color: 'var(--text-3)', fontFamily: 'var(--mono)',
              }}>{tag}</span>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {messages.map(msg => (
            <ChatMessage key={msg.id} message={msg} />
          ))}

          {isLoading && (
            <div className="fade-up" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <div style={{
                width: 32, height: 32, borderRadius: '10px',
                background: 'linear-gradient(135deg, var(--accent), var(--purple))',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px',
              }}>🤖</div>
              <div style={{
                background: 'var(--bg-card)', border: '1px solid var(--border)',
                borderRadius: '18px 18px 18px 4px', padding: '12px 16px',
                display: 'flex', gap: '4px', alignItems: 'center',
              }}>
                {[0, 0.2, 0.4].map((delay, i) => (
                  <div key={i} style={{
                    width: 6, height: 6, borderRadius: '50%', background: 'var(--text-3)',
                    animation: `pulse 1.2s ease ${delay}s infinite`,
                  }} />
                ))}
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {showPrompts && messages.length <= 2 && <QuickPrompts onSelect={handleSend} />}
        <ChatInput onSend={handleSend} isLoading={isLoading} taskRunning={taskRunning} />
      </div>
    </div>
  );
}
