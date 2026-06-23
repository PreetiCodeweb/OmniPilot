import LogStream from './LogStream';
import PlatformBadge from './PlatformBadge';

export default function ChatMessage({ message }) {
  const { role, content, type, logs, platform, done, error, task } = message;

  if (type === 'logs') {
    return (
      <div className="fade-up" style={{ paddingLeft: '0' }}>
        <LogStream logs={logs} platform={platform} done={done} error={error} />
      </div>
    );
  }

  const isUser = role === 'user';

  return (
    <div className="fade-up" style={{
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      gap: '10px',
      alignItems: 'flex-end',
    }}>
      {/* Avatar */}
      {!isUser && (
        <div style={{
          width: 32, height: 32,
          borderRadius: '10px',
          background: 'linear-gradient(135deg, var(--accent), var(--purple))',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '14px', flexShrink: 0,
        }}>🤖</div>
      )}

      {/* Bubble */}
      <div style={{ maxWidth: '78%' }}>
        {task?.platform && !isUser && (
          <div style={{ marginBottom: '6px' }}>
            <PlatformBadge platform={task.platform} />
          </div>
        )}
        <div style={{
          background: isUser
            ? 'linear-gradient(135deg, var(--accent), #1a4fd6)'
            : 'var(--bg-card)',
          color: 'var(--text-1)',
          border: isUser ? 'none' : '1px solid var(--border)',
          borderRadius: isUser
            ? '18px 18px 4px 18px'
            : '18px 18px 18px 4px',
          padding: '12px 16px',
          fontSize: '14px',
          lineHeight: 1.6,
          boxShadow: isUser ? '0 2px 12px #2e68ff33' : 'none',
        }}>
          {content}
        </div>
      </div>

      {/* User avatar */}
      {isUser && (
        <div style={{
          width: 32, height: 32,
          borderRadius: '10px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '14px', flexShrink: 0,
        }}>👤</div>
      )}
    </div>
  );
}
