import React, { useState, useRef, useEffect } from 'react';
import { Send, CornerDownLeft, Loader2, Sparkles } from 'lucide-react';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  isLoading,
  disabled = false,
}) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading || disabled) return;
    onSendMessage(trimmed);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-4">
      <div className="relative bg-white border border-slate-200 focus-within:border-indigo-500 rounded-2xl shadow-sm focus-within:shadow-md transition-all duration-200">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about Zyro Dynamics HR policies (e.g., leave, payroll, benefits)..."
          rows={1}
          disabled={disabled || isLoading}
          className="w-full pl-4 pr-14 py-3.5 bg-transparent resize-none outline-none text-slate-800 placeholder-slate-400 text-sm leading-relaxed max-h-44 disabled:opacity-50"
        />

        <div className="absolute right-2 bottom-2">
          <button
            type="button"
            onClick={handleSend}
            disabled={!input.trim() || isLoading || disabled}
            aria-label="Send message"
            className="inline-flex items-center justify-center w-9 h-9 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 text-white disabled:text-slate-400 transition-colors duration-150 shadow-sm"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between mt-2 px-2 text-[11px] text-slate-400">
        <span className="flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-indigo-500" />
          Strictly grounded in Zyro Dynamics HR policy PDFs
        </span>
        <span className="hidden sm:inline-flex items-center gap-1">
          <CornerDownLeft className="w-2.5 h-2.5" />
          <span>Press Enter to send, Shift + Enter for new line</span>
        </span>
      </div>
    </div>
  );
};

