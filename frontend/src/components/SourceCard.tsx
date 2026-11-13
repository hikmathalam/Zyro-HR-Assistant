import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { SourceCitation } from '@/types/chat';

interface SourceCardProps {
  sources: SourceCitation[];
}

export const SourceCard: React.FC<SourceCardProps> = ({ sources }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (!sources || sources.length === 0) return null;

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <div className="mt-3 pt-3 border-t border-slate-100">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
        <FileText className="w-3.5 h-3.5 text-indigo-600" />
        <span>Verified HR Policy Citations ({sources.length})</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {sources.map((src, idx) => {
          const isExpanded = expandedIndex === idx;
          const cleanName = src.file.replace(/^\d+_/, '').replace(/\.pdf$/i, '').replace(/_/g, ' ');

          return (
            <div
              key={`${src.file}-${src.page}-${idx}`}
              className="bg-slate-50 border border-slate-200 hover:border-indigo-300 rounded-lg text-xs transition-colors duration-150 overflow-hidden"
            >
              <button
                type="button"
                onClick={() => toggleExpand(idx)}
                className="flex items-center gap-2 px-2.5 py-1.5 text-left text-slate-700 hover:text-indigo-700 font-medium"
              >
                <span className="inline-flex items-center justify-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-indigo-100 text-indigo-800">
                  Page {src.page}
                </span>
                <span className="truncate max-w-[200px]" title={src.file}>
                  {cleanName}
                </span>
                {src.snippet && (
                  isExpanded ? <ChevronUp className="w-3 h-3 text-slate-400" /> : <ChevronDown className="w-3 h-3 text-slate-400" />
                )}
              </button>

              {isExpanded && src.snippet && (
                <div className="px-3 py-2 bg-white border-t border-slate-200 text-slate-600 text-[11px] leading-relaxed max-w-md">
                  <div className="font-semibold text-slate-800 mb-1 flex items-center justify-between">
                    <span>Excerpt ({src.file})</span>
                  </div>
                  <p className="italic bg-slate-50 p-2 rounded border border-slate-100 font-sans">
                    "{src.snippet}"
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

