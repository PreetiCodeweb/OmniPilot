import { useEffect, useRef } from 'react';
import PlatformBadge from './PlatformBadge';

export default function LogStream({ logs = [], platform, done, error }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const statusColor = error ? 'var(--red)' : done ? 'var(--green)' : 'var(--accent)';
  const statusLabel = error ? 'FAILED' : done ? 'DONE' : 'RUNNING';

  return (
    <div style={{
      background: 'var(--bg)',
      border: `1px solid ${error ? 'var(--red)44' : done ? 'var(--green)44' : 'var(--border-glow)'}`,
      borderRadius: 'var(--radius)',
      overflow: 'hidden',
      marginTop: '8px',
    }}>
      {/* Header bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '8px 14px',
        background: 'var(--bg-surface)',
        borderBottom: '1px solid var(--border)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: 7, height: 7,
            borderRadius: '50%',
            background: statusColor,
            animation: done || error ? 'none' : 'pulse 1.2s ease infinite',
          }} />
          <span style={{ fontSize: '11px', fontFamily: 'var(--mono)', color: 'var(--text-2)' }}>
            AGENT LOGS
          </span>
          {platform && <PlatformBadge platform={platform} />}
        </div>
        <span style={{
          fontSize: '10px',
          fontFamily: 'var(--mono)',
          color: statusColor,
          fontWeight: 600,
          letterSpacing: '0.08em',
        }}>
          {statusLabel}
        </span>
      </div>

      {/* Log lines */}
      <div style={{
        padding: '12px 14px',
        maxHeight: '220px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
      }}>
        {logs.length === 0 && (
          <span style={{ color: 'var(--text-3)', fontFamily: 'var(--mono)', fontSize: '12px' }}>
            Waiting for agent...
          </span>
        )}
        {logs.map((log, i) => (
          <div key={i} style={{
            fontFamily: 'var(--mono)',
            fontSize: '12px',
            lineHeight: 1.6,
            color: log.startsWith('❌') ? 'var(--red)'
                 : log.startsWith('✅') ? 'var(--green)'
                 : log.startsWith('⚠️') ? 'var(--yellow)'
                 : log.startsWith('🤖') ? 'var(--purple)'
                 : 'var(--text-2)',
            animation: 'fadeUp 0.2s ease both',
          }}>
            {log}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
