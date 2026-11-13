'use client';

import React, { useState } from 'react';
import {
  Menu,
  X,
  Trash2,
  Sparkles,
  ShieldCheck,
  Building2,
  Info,
  HelpCircle,
} from 'lucide-react';
import { Sidebar } from '@/components/Sidebar';
import { MessageList } from '@/components/MessageList';
import { MessageInput } from '@/components/MessageInput';
import { SuggestedQuestions } from '@/components/SuggestedQuestions';
import { useChat } from '@/hooks/useChat';

export default function Home() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const {
    messages,
    isLoading,
    error,
    health,
    sendMessage,
    clearChat,
    conversations,
    selectConversation,
    currentConvoId,
  } = useChat();

  const handleSelectSuggestedQuestion = (question: string) => {
    sendMessage(question);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-100">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex md:shrink-0">
        <Sidebar
          onNewChat={clearChat}
          conversations={conversations}
          currentConvoId={currentConvoId}
          onSelectConversation={selectConversation}
          health={health}
          onSelectCategoryPrompt={sendMessage}
        />
      </div>

      {/* Mobile Drawer Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          <div
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="relative flex-1 flex flex-col max-w-xs w-full bg-slate-900 z-10">
            <div className="absolute top-2 right-2 p-1">
              <button
                type="button"
                onClick={() => setMobileMenuOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <Sidebar
              onNewChat={() => {
                clearChat();
                setMobileMenuOpen(false);
              }}
              conversations={conversations}
              currentConvoId={currentConvoId}
              onSelectConversation={(c) => {
                selectConversation(c);
                setMobileMenuOpen(false);
              }}
              health={health}
              onSelectCategoryPrompt={(p) => {
                sendMessage(p);
                setMobileMenuOpen(false);
              }}
            />
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-slate-50">
        {/* Top Header Bar */}
        <header className="h-16 px-4 sm:px-6 bg-white border-b border-slate-200 flex items-center justify-between shrink-0 shadow-xs">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(true)}
              className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100"
            >
              <Menu className="w-5 h-5" />
            </button>

            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-semibold text-slate-900 text-sm sm:text-base">
                  Zyro HR Help Desk
                </h2>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                  Official HR RAG
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                Zyro Dynamics Pvt. Ltd. • Grounded in 11 Verified HR Policy Documents
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <button
                type="button"
                onClick={clearChat}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:text-rose-600 hover:border-rose-200 hover:bg-rose-50 text-xs font-medium transition-colors"
                title="Clear current conversation"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Clear Chat</span>
              </button>
            )}
          </div>
        </header>

        {/* Chat Content Body */}
        <div className="flex-1 overflow-y-auto flex flex-col justify-between">
          {messages.length === 0 ? (
            <div className="flex-1 flex flex-col justify-center items-center px-4 py-8 max-w-3xl mx-auto w-full text-center">
              {/* Welcome Badge & Greeting */}
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200/60 text-indigo-700 text-xs font-semibold mb-4 shadow-xs">
                <Sparkles className="w-3.5 h-3.5" />
                <span>AI-Powered Enterprise Help Desk</span>
              </div>

              <h3 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Welcome to <span className="text-indigo-600">Zyro HR Assistant</span>
              </h3>

              <p className="mt-2 text-sm text-slate-600 max-w-xl leading-relaxed">
                Your trusted, private assistant for Zyro Dynamics Pvt. Ltd. policy questions.
                Ask about leave balances, payroll schedules, wellness allowance, gratuity, POSH procedures, or separation rules.
              </p>

              {/* Trust & Guardrail Pillars */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 my-6 w-full text-left">
                <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-xs">
                  <div className="flex items-center gap-2 text-indigo-600 font-semibold text-xs mb-1">
                    <ShieldCheck className="w-4 h-4" />
                    <span>Zero Hallucinations</span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Strictly grounded in official HR PDFs. Refuses unsupported or out-of-scope queries.
                  </p>
                </div>

                <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-xs">
                  <div className="flex items-center gap-2 text-indigo-600 font-semibold text-xs mb-1">
                    <Building2 className="w-4 h-4" />
                    <span>Exact Source Citations</span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Every answer references the exact PDF document code, title, and page number.
                  </p>
                </div>

                <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-xs">
                  <div className="flex items-center gap-2 text-indigo-600 font-semibold text-xs mb-1">
                    <Sparkles className="w-4 h-4" />
                    <span>Instant Answers</span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    High-speed Groq LLM inference with FAISS Maximum Marginal Relevance (MMR).
                  </p>
                </div>
              </div>

              {/* Suggested Questions */}
              <SuggestedQuestions
                onSelectQuestion={handleSelectSuggestedQuestion}
                disabled={isLoading}
              />
            </div>
          ) : (
            <MessageList messages={messages} isLoading={isLoading} />
          )}

          {/* Sticky Input Footer */}
          <MessageInput
            onSendMessage={sendMessage}
            isLoading={isLoading}
          />
        </div>
      </main>
    </div>
  );
}

