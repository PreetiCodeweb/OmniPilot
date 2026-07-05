const PLATFORMS = {
  twitter:   { label: 'Twitter / X', color: '#1d9bf0', icon: 'X' },
  linkedin:  { label: 'LinkedIn',    color: '#0a66c2', icon: 'in' },
  reddit:    { label: 'Reddit',      color: '#ff4500', icon: 'r/' },
  whatsapp:  { label: 'WhatsApp',    color: '#22d98a', icon: 'WA' },
};

export default function PlatformBadge({ platform }) {
  const p = PLATFORMS[platform?.toLowerCase()] || { label: platform, color: '#9b7fff', icon: 'AI' };
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '5px',
      background: p.color + '20',
      color: p.color,
      border: `1px solid ${p.color}44`,
      borderRadius: '6px',
      padding: '2px 8px',
      fontSize: '11px',
      fontWeight: 600,
      fontFamily: 'var(--mono)',
      letterSpacing: '0.04em',
    }}>
      <span style={{ fontSize: '10px' }}>{p.icon}</span>
      {p.label.toUpperCase()}
    </span>
  );
}
