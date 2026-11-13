import React from 'react';
import { HelpCircle, ArrowUpRight } from 'lucide-react';

interface SuggestedQuestionsProps {
  onSelectQuestion: (question: string) => void;
  disabled?: boolean;
}

const SUGGESTED_QUESTIONS = [
  {
    category: "Leave Policy",
    text: "How does Earned Leave accrue every month?",
  },
  {
    category: "Payroll",
    text: "When is monthly salary credited?",
  },
  {
    category: "Benefits",
    text: "What is the annual wellness allowance?",
  },
  {
    category: "Wellness & Support",
    text: "How many counselling sessions are available?",
  },
  {
    category: "Separation",
    text: "Can employees take leave during notice period?",
  },
];

export const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({
  onSelectQuestion,
  disabled = false,
}) => {
  return (
    <div className="w-full max-w-3xl mx-auto my-6 px-4">
      <div className="flex items-center gap-2 mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
        <HelpCircle className="w-3.5 h-3.5 text-indigo-600" />
        <span>Frequently Asked HR Questions</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
        {SUGGESTED_QUESTIONS.map((q, idx) => (
          <button
            key={idx}
            type="button"
            disabled={disabled}
            onClick={() => onSelectQuestion(q.text)}
            className="group flex items-start justify-between p-3 text-left bg-white hover:bg-indigo-50/60 border border-slate-200 hover:border-indigo-300 rounded-xl transition-all duration-200 shadow-sm hover:shadow"
          >
            <div>
              <span className="inline-block text-[10px] font-semibold tracking-wide uppercase px-1.5 py-0.5 rounded bg-slate-100 group-hover:bg-indigo-100 text-slate-600 group-hover:text-indigo-700 mb-1">
                {q.category}
              </span>
              <p className="text-xs text-slate-700 group-hover:text-indigo-950 font-medium">
                {q.text}
              </p>
            </div>
            <ArrowUpRight className="w-4 h-4 text-slate-300 group-hover:text-indigo-600 shrink-0 mt-0.5 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
          </button>
        ))}
      </div>
    </div>
  );
};

