const PROMPTS = [
  { icon: '𝕏',  label: 'Follow trading accounts', text: 'Follow top 10 trading and stock market accounts on Twitter', color: '#1d9bf0' },
  { icon: 'in', label: 'LinkedIn: coding channels', text: 'Follow top software engineering and AI companies on LinkedIn', color: '#0a66c2' },
  { icon: '👾', label: 'Reddit: subscribe coding', text: 'Subscribe to the best coding and programming subreddits', color: '#ff4500' },
  { icon: '💬', label: 'WhatsApp message', text: "Send a WhatsApp to ", color: '#22d98a' },
  { icon: '📈', label: 'Business subreddits', text: 'Subscribe to business, startup and entrepreneurship subreddits', color: '#f5c518' },
  { icon: '🤖', label: 'Follow AI channels', text: 'Follow top AI and machine learning accounts on Twitter', color: '#9b7fff' },
];

export default function QuickPrompts({ onSelect }) {
  return (
    <div style={{
      padding: '0 20px 16px',
      display: 'flex',
      flexWrap: 'wrap',
      gap: '8px',
    }}>
      <p style={{
        width: '100%',
        fontSize: '11px',
        color: 'var(--text-3)',
        fontWeight: 500,
        letterSpacing: '0.06em',
        marginBottom: '4px',
      }}>QUICK ACTIONS</p>
      {PROMPTS.map((p, i) => (
        <button
          key={i}
          onClick={() => onSelect(p.text)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: 'var(--bg-card)',
            border: `1px solid var(--border)`,
            borderRadius: '20px',
            padding: '6px 13px',
            fontSize: '12px',
            color: 'var(--text-2)',
            cursor: 'pointer',
            transition: 'var(--transition)',
            fontFamily: 'var(--font)',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.borderColor = p.color + '66';
            e.currentTarget.style.color = p.color;
            e.currentTarget.style.background = p.color + '10';
          }}
          onMouseLeave={e => {
            e.currentTarget.style.borderColor = 'var(--border)';
            e.currentTarget.style.color = 'var(--text-2)';
            e.currentTarget.style.background = 'var(--bg-card)';
          }}
        >
          <span style={{ fontSize: '11px' }}>{p.icon}</span>
          {p.label}
        </button>
      ))}
    </div>
  );
}
