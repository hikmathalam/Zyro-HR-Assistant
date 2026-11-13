import React from 'react';
import {
  PlusCircle,
  MessageSquare,
  BookOpen,
  ShieldCheck,
  Building2,
  FileText,
  Activity,
  Layers,
  Sparkles,
  HelpCircle,
  Cpu
} from 'lucide-react';
import { Conversation, HealthResponse } from '@/types/chat';

interface SidebarProps {
  onNewChat: () => void;
  conversations: Conversation[];
  currentConvoId: string;
  onSelectConversation: (convo: Conversation) => void;
  health: HealthResponse | null;
  onSelectCategoryPrompt?: (prompt: string) => void;
}

const HR_POLICY_DOCUMENTS = [
  { name: 'Leave Policy', code: 'ZDL-HR-002', prompt: 'What are the rules and limits for Earned Leave and Casual Leave?' },
  { name: 'Compensation & Benefits', code: 'ZDL-HR-006', prompt: 'What are the employee benefits, wellness allowance, and gratuity criteria?' },
  { name: 'Work From Home Policy', code: 'ZDL-HR-003', prompt: 'What is the company work from home and remote work policy?' },
  { name: 'Code of Conduct', code: 'ZDL-HR-004', prompt: 'What does the company Code of Conduct state regarding workplace ethics?' },
  { name: 'IT & Data Security', code: 'ZDL-HR-007', prompt: 'What are the key IT security and password requirements?' },
  { name: 'POSH Policy', code: 'ZDL-HR-005', prompt: 'What is the procedure for filing a complaint under the POSH policy?' },
  { name: 'Onboarding & Separation', code: 'ZDL-HR-008', prompt: 'What is the notice period requirement and separation process?' },
  { name: 'Travel & Expense', code: 'ZDL-HR-010', prompt: 'What expenses are eligible for reimbursement under the travel policy?' },
];

export const Sidebar: React.FC<SidebarProps> = ({
  onNewChat,
  conversations,
  currentConvoId,
  onSelectConversation,
  health,
  onSelectCategoryPrompt,
}) => {
  return (
    <aside className="w-72 bg-slate-900 text-slate-200 flex flex-col h-full border-r border-slate-800 select-none">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center text-white shadow-md font-bold text-lg tracking-wider">
            Z
          </div>
          <div>
            <h1 className="font-bold text-sm text-white tracking-tight flex items-center gap-1.5">
              Zyro HR Assistant
              <span className="text-[10px] uppercase font-semibold px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                RAG
              </span>
            </h1>
            <p className="text-[11px] text-slate-400 flex items-center gap-1">
              <Building2 className="w-3 h-3 text-slate-500" />
              Zyro Dynamics Pvt. Ltd.
            </p>
          </div>
        </div>

        {/* New Chat Button */}
        <button
          type="button"
          onClick={onNewChat}
          className="mt-4 w-full flex items-center justify-center gap-2 px-3.5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-sm transition-all duration-150"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Conversation</span>
        </button>
      </div>

      {/* Middle Scrollable Section */}
      <div className="flex-1 overflow-y-auto p-3 space-y-5">
        {/* Recent Conversations */}
        <div>
          <div className="px-2 mb-1.5 flex items-center justify-between text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            <span className="flex items-center gap-1.5">
              <MessageSquare className="w-3 h-3 text-indigo-400" />
              Recent Conversations
            </span>
            <span className="text-[10px] text-slate-500">{conversations.length}</span>
          </div>

          <div className="space-y-1">
            {conversations.length === 0 ? (
              <p className="px-2 py-2 text-xs text-slate-500 italic">No recent chats yet.</p>
            ) : (
              conversations.map((convo) => (
                <button
                  key={convo.id}
                  type="button"
                  onClick={() => onSelectConversation(convo)}
                  className={`w-full text-left px-2.5 py-2 rounded-lg text-xs truncate transition-colors flex items-center gap-2 ${
                    convo.id === currentConvoId
                      ? 'bg-slate-800 text-indigo-300 font-medium'
                      : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                  }`}
                >
                  <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-70" />
                  <span className="truncate">{convo.title}</span>
                </button>
              ))
            )}
          </div>
        </div>

        {/* HR Policy Categories */}
        <div>
          <div className="px-2 mb-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <BookOpen className="w-3 h-3 text-indigo-400" />
            Official HR Policies
          </div>

          <div className="space-y-1">
            {HR_POLICY_DOCUMENTS.map((doc, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => onSelectCategoryPrompt && onSelectCategoryPrompt(doc.prompt)}
                className="w-full text-left px-2.5 py-1.5 rounded-lg text-xs text-slate-400 hover:bg-slate-800/70 hover:text-slate-200 transition-colors flex items-center justify-between group"
              >
                <div className="flex items-center gap-2 truncate">
                  <FileText className="w-3.5 h-3.5 text-slate-500 group-hover:text-indigo-400 shrink-0" />
                  <span className="truncate">{doc.name}</span>
                </div>
                <span className="text-[9px] font-mono text-slate-500 group-hover:text-slate-400">
                  {doc.code}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* System Status Footer */}
      <div className="p-3 bg-slate-950 border-t border-slate-800/80 text-[11px] text-slate-400">
        <div className="flex items-center justify-between mb-1.5">
          <span className="flex items-center gap-1.5 font-medium text-slate-300">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            RAG Pipeline Status
          </span>
          <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold ${
            health?.index_loaded ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
          }`}>
            {health?.index_loaded ? 'Index Ready' : 'Connecting'}
          </span>
        </div>

        <div className="flex items-center justify-between text-[10px] text-slate-500">
          <span className="flex items-center gap-1">
            <Layers className="w-3 h-3" />
            Indexed Chunks
          </span>
          <span className="font-mono text-slate-300">
            {health?.total_indexed_chunks ?? 91}
          </span>
        </div>

        <div className="flex items-center justify-between text-[10px] text-slate-500 mt-0.5">
          <span className="flex items-center gap-1">
            <Cpu className="w-3 h-3" />
            Groq Model
          </span>
          <span className="font-mono text-indigo-400 truncate max-w-[120px]" title={health?.model}>
            {health?.model ? health.model.replace('-versatile', '') : 'llama-3.3-70b'}
          </span>
        </div>
      </div>
    </aside>
  );
};

