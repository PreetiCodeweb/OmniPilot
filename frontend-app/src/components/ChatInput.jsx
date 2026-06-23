import { useState, useRef, useEffect } from 'react';

export default function ChatInput({ onSend, isLoading, taskRunning }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  const disabled = isLoading || taskRunning;

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 140) + 'px';
    }
  }, [text]);

  const submit = () => {
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setText('');
    }
  };

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div style={{
      padding: '16px 20px 20px',
      borderTop: '1px solid var(--border)',
      background: 'var(--bg-surface)',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'flex-end',
        gap: '10px',
        background: 'var(--bg-input)',
        border: `1px solid ${disabled ? 'var(--border)' : 'var(--border-glow)'}`,
        borderRadius: '16px',
        padding: '10px 10px 10px 16px',
        transition: 'var(--transition)',
      }}>
        <textarea
          ref={textareaRef}
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={onKey}
          disabled={disabled}
          placeholder={
            taskRunning
              ? '⏳ Agent is running, please wait...'
              : isLoading
              ? '🧠 Thinking...'
              : 'Tell me what to do — "Follow top trading accounts on Twitter"'
          }
          rows={1}
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: 'var(--text-1)',
            fontFamily: 'var(--font)',
            fontSize: '14px',
            lineHeight: 1.6,
            resize: 'none',
            maxHeight: '140px',
            overflowY: 'auto',
            opacity: disabled ? 0.5 : 1,
          }}
        />

        <button
          onClick={submit}
          disabled={disabled || !text.trim()}
          style={{
            width: 38, height: 38,
            borderRadius: '10px',
            background: disabled || !text.trim()
              ? 'var(--border)'
              : 'linear-gradient(135deg, var(--accent), #1a4fd6)',
            border: 'none',
            cursor: disabled || !text.trim() ? 'not-allowed' : 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '16px',
            flexShrink: 0,
            transition: 'var(--transition)',
            boxShadow: disabled || !text.trim() ? 'none' : '0 2px 12px #2e68ff44',
          }}
        >
          {isLoading ? (
            <div style={{
              width: 14, height: 14,
              border: '2px solid white',
              borderTopColor: 'transparent',
              borderRadius: '50%',
              animation: 'spin 0.8s linear infinite',
            }} />
          ) : '↑'}
        </button>
      </div>

      <p style={{
        textAlign: 'center',
        fontSize: '10px',
        color: 'var(--text-3)',
        marginTop: '10px',
        fontFamily: 'var(--mono)',
      }}>
        Enter to send · Shift+Enter for new line · Powered by Claude + Browser Use
      </p>
    </div>
  );
}
