import { useEffect, useState } from 'react';
import { checkHealth } from '../utils/api';

const PLATFORMS = [
  { name: 'Twitter / X',  icon: '𝕏',   color: '#1d9bf0', desc: 'Follow trading & coding accounts' },
  { name: 'LinkedIn',     icon: 'in',   color: '#0a66c2', desc: 'Connect with business channels' },
  { name: 'Reddit',       icon: '👾',   color: '#ff4500', desc: 'Subscribe to subreddits' },
  { name: 'WhatsApp',     icon: '💬',   color: '#22d98a', desc: 'Send messages to contacts' },
];

const EXAMPLES = [
  '"Follow 15 trading accounts on Twitter"',
  '"Subscribe to python and ML subreddits"',
  '"Follow AI companies on LinkedIn"',
  '"Send WhatsApp to Riya: be there in 10 mins"',
];

export default function Sidebar({ taskRunning }) {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    checkHealth().then(setHealth);
    const t = setInterval(() => checkHealth().then(setHealth), 15000);
    return () => clearInterval(t);
  }, []);

  const isOnline = health?.status === 'ok';

  return (
    <aside style={{
      width: 260,
      flexShrink: 0,
      background: 'var(--bg-surface)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      padding: '24px 0',
      gap: '28px',
      overflowY: 'auto',
    }}>
      {/* Logo */}
      <div style={{ padding: '0 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: 36, height: 36,
            background: 'linear-gradient(135deg, var(--accent), var(--purple))',
            borderRadius: '10px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '18px',
          }}>🤖</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '15px', letterSpacing: '-0.02em' }}>Social AI</div>
            <div style={{ fontSize: '11px', color: 'var(--text-3)' }}>Automation Agent</div>
          </div>
        </div>
      </div>

      {/* Backend status */}
      <div style={{ padding: '0 20px' }}>
        <div style={{
          background: 'var(--bg-card)',
          border: `1px solid ${isOnline ? 'var(--green)33' : 'var(--red)33'}`,
          borderRadius: 'var(--radius)',
          padding: '10px 14px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
        }}>
          <div style={{
            width: 8, height: 8,
            borderRadius: '50%',
            background: isOnline ? 'var(--green)' : 'var(--red)',
            animation: isOnline ? 'pulse 2s ease infinite' : 'none',
          }} />
          <div>
            <div style={{ fontSize: '12px', fontWeight: 600, color: isOnline ? 'var(--green)' : 'var(--red)' }}>
              {isOnline ? 'Backend Online' : 'Backend Offline'}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-3)', fontFamily: 'var(--mono)' }}>
              {isOnline ? health.llm_provider?.toUpperCase() : 'python main.py'}
            </div>
          </div>
        </div>

        {taskRunning && (
          <div style={{
            marginTop: '8px',
            background: 'var(--accent-soft)',
            border: '1px solid var(--border-glow)',
            borderRadius: 'var(--radius)',
            padding: '10px 14px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}>
            <div style={{
              width: 14, height: 14,
              border: '2px solid var(--accent)',
              borderTopColor: 'transparent',
              borderRadius: '50%',
              animation: 'spin 0.8s linear infinite',
            }} />
            <span style={{ fontSize: '12px', color: 'var(--accent)', fontWeight: 600 }}>
              Agent Running...
            </span>
          </div>
        )}
      </div>

      {/* Platforms */}
      <div style={{ padding: '0 20px' }}>
        <p style={{ fontSize: '10px', color: 'var(--text-3)', fontWeight: 600, letterSpacing: '0.08em', marginBottom: '10px' }}>
          PLATFORMS
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {PLATFORMS.map(p => (
            <div key={p.name} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '8px 10px',
              borderRadius: '8px',
              background: 'var(--bg-card)',
            }}>
              <span style={{
                width: 28, height: 28,
                background: p.color + '20',
                borderRadius: '8px',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '11px',
                fontWeight: 700,
                color: p.color,
              }}>{p.icon}</span>
              <div>
                <div style={{ fontSize: '12px', fontWeight: 600 }}>{p.name}</div>
                <div style={{ fontSize: '10px', color: 'var(--text-3)' }}>{p.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Example prompts */}
      <div style={{ padding: '0 20px' }}>
        <p style={{ fontSize: '10px', color: 'var(--text-3)', fontWeight: 600, letterSpacing: '0.08em', marginBottom: '10px' }}>
          EXAMPLE PROMPTS
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {EXAMPLES.map((ex, i) => (
            <div key={i} style={{
              fontSize: '11px',
              color: 'var(--text-3)',
              fontFamily: 'var(--mono)',
              lineHeight: 1.5,
              padding: '6px 0',
              borderBottom: '1px solid var(--border)',
            }}>{ex}</div>
          ))}
        </div>
      </div>
    </aside>
  );
}
