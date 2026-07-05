import { useState, useCallback, useRef } from 'react';
import { sendChat, connectTaskSocket } from '../utils/api';

let msgId = 0;
const uid = () => ++msgId;

export function useChat() {
  const [messages, setMessages] = useState([
    {
      id: uid(),
      role: 'assistant',
      content: "Hey Preeti. I can control Twitter, LinkedIn, Reddit, and WhatsApp through a real browser once the backend status panel shows the needed keys and browser tools are ready. Tell me an action in plain English.",
      type: 'text',
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [taskRunning, setTaskRunning] = useState(false);
  const wsRef = useRef(null);

  const addMessage = useCallback((msg) => {
    setMessages(prev => [...prev, { id: uid(), ...msg }]);
  }, []);

  const send = useCallback(async (text) => {
    if (!text.trim() || isLoading) return;

    addMessage({ role: 'user', content: text, type: 'text' });
    setIsLoading(true);

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
      } else if (task?.preflight?.length) {
        addMessage({
          role: 'system',
          type: 'logs',
          logs: task.preflight.map(issue => `❌ ${issue}`),
          platform: task.platform,
          error: true,
          done: true,
        });
      }
    } catch (err) {
      addMessage({
        role: 'assistant',
        content: `Error: ${err.message}. Start the backend with uvicorn main:app --host 127.0.0.1 --port 8000 from the backend folder.`,
        type: 'text',
      });
      setTaskRunning(false);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, addMessage]);

  return { messages, isLoading, taskRunning, send };
}
