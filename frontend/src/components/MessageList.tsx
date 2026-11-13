import React, { useRef, useEffect } from 'react';
import { Bot, User, ShieldAlert, Sparkles } from 'lucide-react';
import { Message } from '@/types/chat';
import { SourceCard } from './SourceCard';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 max-w-4xl mx-auto w-full">
      {messages.map((message) => {
        const isUser = message.role === 'user';

        return (
          <div
            key={message.id}
            className={`flex gap-3.5 ${isUser ? 'justify-end' : 'justify-start'}`}
          >
            {!isUser && (
              <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white shrink-0 shadow-sm mt-0.5">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div
              className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 shadow-sm ${
                isUser
                  ? 'bg-indigo-600 text-white rounded-br-none'
                  : message.isRefusal
                  ? 'bg-amber-50/70 border border-amber-200 text-slate-800 rounded-bl-none'
                  : 'bg-white border border-slate-200 text-slate-800 rounded-bl-none'
              }`}
            >
              {message.isRefusal && !isUser && (
                <div className="flex items-center gap-1.5 text-amber-700 text-xs font-semibold mb-1">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  <span>Out of Scope / Unsupported Question</span>
                </div>
              )}

              <div className="text-sm leading-relaxed whitespace-pre-wrap font-normal">
                {message.content}
              </div>

              {/* Source citations */}
              {message.sources && message.sources.length > 0 && (
                <SourceCard sources={message.sources} />
              )}

              <div
                className={`text-[10px] mt-1.5 text-right ${
                  isUser ? 'text-indigo-200' : 'text-slate-400'
                }`}
              >
                {message.timestamp}
              </div>
            </div>

            {isUser && (
              <div className="w-8 h-8 rounded-xl bg-slate-200 flex items-center justify-center text-slate-600 shrink-0 shadow-sm mt-0.5">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        );
      })}

      {/* Loading state indicator */}
      {isLoading && (
        <div className="flex gap-3.5 justify-start">
          <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white shrink-0 shadow-sm animate-pulse">
            <Bot className="w-4 h-4" />
          </div>
          <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-none px-4 py-3.5 shadow-sm">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-slate-500">Searching HR Policy Documents</span>
              <div className="flex space-x-1">
                <div className="w-1.5 h-1.5 bg-indigo-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-1.5 h-1.5 bg-indigo-600 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-1.5 h-1.5 bg-indigo-600 rounded-full animate-bounce"></div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
};

