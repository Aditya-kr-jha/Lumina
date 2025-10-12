import { createContext, useState, useContext, useCallback } from 'react';
import {
  sendChatQuery,
  getChatHistory,
  deleteChatSession,
  clearAllSessions,
} from '../services/chatService';

const ChatContext = createContext(null);

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const startNewChat = useCallback(() => {
    setMessages([]);
    setSessionId(crypto.randomUUID());
    setError(null);
  }, []);

  const sendMessage = async (question, documentId) => {
    if (!sessionId) {
      setSessionId(crypto.randomUUID());
    }

    try {
      setError(null);
      
      // Add user message immediately
      const userMessage = {
        role: 'user',
        content: question,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      
      setLoading(true);

      // Send query to API
      const data = await sendChatQuery({
        question,
        document_id: documentId,
        session_id: sessionId,
        include_sources: true,
      });

      // Add AI response
      const aiMessage = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources || [],
        timestamp: data.timestamp,
        processing_time: data.processing_time,
      };
      setMessages((prev) => [...prev, aiMessage]);

      return { success: true, data };
    } catch (err) {
      console.error('Failed to send message:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to send message';
      setError(errorMessage);
      
      // Remove the user message if request failed
      setMessages((prev) => prev.slice(0, -1));
      
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const regenerateLastMessage = async (documentId) => {
    if (messages.length < 2) return;

    // Get the last user message
    const lastUserMessage = [...messages]
      .reverse()
      .find((msg) => msg.role === 'user');

    if (!lastUserMessage) return;

    // Remove last AI response
    setMessages((prev) => prev.slice(0, -1));

    // Resend the question
    return sendMessage(lastUserMessage.content, documentId);
  };

  const loadChatHistory = async (sessionIdToLoad) => {
    try {
      setLoading(true);
      setError(null);

      const data = await getChatHistory(sessionIdToLoad);
      
      // Convert history to messages format
      const historyMessages = [];
      data.history.forEach((interaction) => {
        historyMessages.push({
          role: 'user',
          content: interaction.question,
        });
        historyMessages.push({
          role: 'assistant',
          content: interaction.answer,
          sources: interaction.sources || [],
        });
      });

      setMessages(historyMessages);
      setSessionId(sessionIdToLoad);

      return { success: true };
    } catch (err) {
      console.error('Failed to load chat history:', err);
      setError(err.response?.data?.detail || 'Failed to load chat history');
      return { success: false, error: err.response?.data?.detail || 'Failed to load chat history' };
    } finally {
      setLoading(false);
    }
  };

  const deleteSession = async (sessionIdToDelete) => {
    try {
      await deleteChatSession(sessionIdToDelete);

      // Clear messages if current session was deleted
      if (sessionIdToDelete === sessionId) {
        startNewChat();
      }

      return { success: true };
    } catch (err) {
      console.error('Failed to delete session:', err);
      return { success: false, error: err.response?.data?.detail || 'Failed to delete session' };
    }
  };

  const clearAll = async () => {
    try {
      await clearAllSessions();
      startNewChat();
      return { success: true };
    } catch (err) {
      console.error('Failed to clear sessions:', err);
      return { success: false, error: err.response?.data?.detail || 'Failed to clear sessions' };
    }
  };

  const value = {
    messages,
    sessionId,
    loading,
    error,
    sendMessage,
    regenerateLastMessage,
    startNewChat,
    loadChatHistory,
    deleteSession,
    clearAll,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

export default ChatContext;
