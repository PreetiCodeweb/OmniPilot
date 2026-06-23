import { useState, useCallback, useRef } from 'react';
import { sendChat, connectTaskSocket } from '../utils/api';

let msgId = 0;
const uid = () => ++msgId;

export function useChat() {
  const [messages, setMessages] = useState([
    {
      id: uid(),
      role: 'assistant',
      content: "Hey Preeti! 👋 I'm your Social AI Agent. Tell me what to do — follow trading accounts on Twitter, subscribe to coding subreddits, connect with business people on LinkedIn, or send a WhatsApp message. Just type naturally!",
      type: 'text',
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeLogs, setActiveLogs] = useState([]);
  const [taskRunning, setTaskRunning] = useState(false);
  const wsRef = useRef(null);

  const addMessage = useCallback((msg) => {
    setMessages(prev => [...prev, { id: uid(), ...msg }]);
  }, []);

  const updateLastLogs = useCallback((log) => {
    setActiveLogs(prev => [...prev, log]);
  }, []);

  const send = useCallback(async (text) => {
    if (!text.trim() || isLoading) return;

    addMessage({ role: 'user', content: text, type: 'text' });
    setIsLoading(true);
    setActiveLogs([]);

    try {
      const { reply, task, task_id } = await sendChat(text);

      addMessage({ role: 'assistant', content: reply, type: 'text', task });

      if (task_id) {
        setTaskRunning(true);
        const logMsgId = uid();
        setMessages(prev => [...prev, {
          id: logMsgId,
          role: 'system',
          type: 'logs',
          logs: [],
          taskId: task_id,
          platform: task?.platform,
        }]);

        const ws = connectTaskSocket(
          task_id,
          (log) => {
            setMessages(prev => prev.map(m =>
              m.id === logMsgId
                ? { ...m, logs: [...(m.logs || []), log] }
                : m
            ));
          },
          (done) => {
            setMessages(prev => prev.map(m =>
              m.id === logMsgId
                ? { ...m, logs: [...(m.logs || []), done], done: true }
                : m
            ));
            setTaskRunning(false);
          },
          (err) => {
            setMessages(prev => prev.map(m =>
              m.id === logMsgId
                ? { ...m, logs: [...(m.logs || []), `❌ ${err}`], error: true }
                : m
            ));
            setTaskRunning(false);
          }
        );
        wsRef.current = ws;
      }
    } catch (err) {
      addMessage({
        role: 'assistant',
        content: `❌ Error: ${err.message}. Is the backend running? (cd backend && python main.py)`,
        type: 'text',
      });
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, addMessage]);

  return { messages, isLoading, taskRunning, send };
}
