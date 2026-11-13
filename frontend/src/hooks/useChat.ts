import { useState, useEffect, useCallback } from 'react';
import { Message, SourceCitation, Conversation, HealthResponse } from '@/types/chat';
import { sendChatMessage, fetchHealth } from '@/lib/api';

const STORAGE_KEY_MESSAGES = 'zyro_hr_messages';
const STORAGE_KEY_CONVOS = 'zyro_hr_conversations';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConvoId, setCurrentConvoId] = useState<string>('default');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);

  // Load health & persisted messages on mount
  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch((err) => console.warn('Could not reach backend health check:', err));

    try {
      const savedMessages = localStorage.getItem(STORAGE_KEY_MESSAGES);
      if (savedMessages) {
        setMessages(JSON.parse(savedMessages));
      }
      const savedConvos = localStorage.getItem(STORAGE_KEY_CONVOS);
      if (savedConvos) {
        setConversations(JSON.parse(savedConvos));
      }
    } catch (e) {
      console.error('Failed to load stored chat history:', e);
    }
  }, []);

  // Save messages to localStorage
  useEffect(() => {
    try {
      if (messages.length > 0) {
        localStorage.setItem(STORAGE_KEY_MESSAGES, JSON.stringify(messages));
      }
    } catch (e) {
      console.error('Failed to save chat to localStorage:', e);
    }
  }, [messages]);

  const sendMessage = useCallback(async (questionText: string) => {
    const trimmed = questionText.trim();
    if (!trimmed || isLoading) return;

    setError(null);

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: trimmed,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const data = await sendChatMessage({ question: trimmed });

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        isRefusal: data.is_refusal,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Update conversations history in sidebar
      setConversations((prev) => {
        const title = trimmed.length > 32 ? `${trimmed.substring(0, 32)}...` : trimmed;
        const existingIdx = prev.findIndex((c) => c.id === currentConvoId);
        const updatedConvo: Conversation = {
          id: currentConvoId,
          title,
          updatedAt: new Date().toLocaleDateString(),
          messages: [...messages, userMessage, assistantMessage],
        };
        const updated = existingIdx >= 0 
          ? [...prev.slice(0, existingIdx), updatedConvo, ...prev.slice(existingIdx + 1)]
          : [updatedConvo, ...prev];
        try {
          localStorage.setItem(STORAGE_KEY_CONVOS, JSON.stringify(updated));
        } catch (_) {}
        return updated;
      });

    } catch (err: any) {
      const errorMsg = err.message || 'Unable to connect to the HR Assistant server.';
      setError(errorMsg);
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Error: ${errorMsg}. Please ensure the backend server is running on http://localhost:8000.`,
        isRefusal: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, currentConvoId, messages]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
    const newId = `convo-${Date.now()}`;
    setCurrentConvoId(newId);
    try {
      localStorage.removeItem(STORAGE_KEY_MESSAGES);
    } catch (_) {}
  }, []);

  const selectConversation = useCallback((convo: Conversation) => {
    setCurrentConvoId(convo.id);
    setMessages(convo.messages);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    health,
    sendMessage,
    clearChat,
    conversations,
    selectConversation,
    currentConvoId,
  };
}

