import React, { useState } from 'react';
import { Bot, Send, Sparkles, Lightbulb, ShieldAlert, ArrowRight, RefreshCw, MessageSquare } from 'lucide-react';
import { askCopilot } from '../services/api';

export default function Copilot() {
  const [messages, setMessages] = useState([
    {
      sender: 'copilot',
      text: "Hello! I am your AI Financial Copilot. Ask me anything about your revenue metrics, customer risk profiles, or suspicious refund activities.",
      insights: [
        "Real-time RAG context active",
        "Automated multi-agent monitoring connected"
      ],
      actions: ["Check high-risk customer profiles", "Inspect recent manual review queue"]
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const samplePrompts = [
    "Why did revenue decrease?",
    "Which customers are high risk?",
    "What refunds look suspicious?",
    "What revenue is recoverable?"
  ];

  const handleSend = async (queryText) => {
    const textToSubmit = queryText || inputQuery;
    if (!textToSubmit.trim() || loading) return;

    const userMsg = { sender: 'user', text: textToSubmit };
    setMessages(prev => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const resp = await askCopilot(textToSubmit);
      const copilotMsg = {
        sender: 'copilot',
        text: resp.answer,
        insights: resp.insights || [],
        actions: resp.suggested_actions || []
      };
      setMessages(prev => [...prev, copilotMsg]);
    } catch (err) {
      setMessages(prev => [...prev, {
        sender: 'copilot',
        text: "Error communicating with AI Copilot. Please check backend connection.",
        insights: [],
        actions: []
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-sky-400" />
            AI Financial Copilot
          </h1>
          <p className="text-sm text-slate-400">Natural language analytical Q&A powered by RAG and multi-agent synthesis.</p>
        </div>
      </div>

      {/* Prompt Chips */}
      <div className="flex flex-wrap gap-2.5">
        {samplePrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            className="bg-[#131c2e] hover:bg-[#1e293b] border border-[#1e293b] hover:border-sky-500/50 text-slate-300 hover:text-white px-3.5 py-1.5 rounded-full text-xs font-medium transition-all flex items-center space-x-1.5"
          >
            <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
            <span>{prompt}</span>
          </button>
        ))}
      </div>

      {/* Chat Conversation Box */}
      <div className="bg-[#131c2e] border border-[#1e293b] rounded-2xl h-[520px] flex flex-col overflow-hidden shadow-2xl">
        <div className="flex-1 p-6 overflow-y-auto space-y-6">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex items-start space-x-3 ${
                msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 ${
                msg.sender === 'user'
                  ? 'bg-sky-600 text-white'
                  : 'bg-gradient-to-tr from-sky-500 to-indigo-600 text-white shadow-md shadow-sky-500/20'
              }`}>
                {msg.sender === 'user' ? 'YOU' : <Bot className="w-5 h-5" />}
              </div>

              <div className={`max-w-[78%] space-y-3 ${
                msg.sender === 'user' ? 'text-right' : ''
              }`}>
                <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-sky-600 text-white font-medium rounded-tr-none'
                    : 'bg-[#0b0f19] border border-[#1e293b] text-slate-200 rounded-tl-none'
                }`}>
                  {msg.text}
                </div>

                {/* Copilot Insights & Suggested Actions */}
                {msg.sender === 'copilot' && (msg.insights?.length > 0 || msg.actions?.length > 0) && (
                  <div className="bg-[#0b0f19] border border-[#1e293b] rounded-xl p-4 space-y-3 text-left">
                    {msg.insights?.length > 0 && (
                      <div>
                        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-1.5">Key Insights</span>
                        <ul className="space-y-1">
                          {msg.insights.map((ins, i) => (
                            <li key={i} className="text-xs text-sky-300 flex items-start space-x-1.5">
                              <span className="text-sky-400 font-bold">•</span>
                              <span>{ins}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {msg.actions?.length > 0 && (
                      <div className="pt-2 border-t border-[#1e293b]">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-1.5">Recommended Platform Actions</span>
                        <ul className="space-y-1">
                          {msg.actions.map((act, i) => (
                            <li key={i} className="text-xs text-emerald-400 flex items-start space-x-1.5 font-medium">
                              <ArrowRight className="w-3 h-3 text-emerald-400 mt-0.5" />
                              <span>{act}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-center space-x-3 text-slate-400 text-xs">
              <Bot className="w-5 h-5 text-sky-400 animate-bounce" />
              <span>Financial Copilot synthesizing data context...</span>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => { e.preventDefault(); handleSend(); }}
          className="p-4 bg-[#0b0f19] border-t border-[#1e293b] flex items-center space-x-3"
        >
          <input
            type="text"
            placeholder="Ask AI Copilot about revenue drops, high risk customers, suspicious refunds..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            className="flex-1 bg-[#131c2e] border border-[#1e293b] text-sm text-white px-4 py-3 rounded-xl focus:outline-none focus:border-sky-500"
          />
          <button
            type="submit"
            disabled={loading || !inputQuery.trim()}
            className="bg-sky-600 hover:bg-sky-500 text-white font-bold p-3 rounded-xl transition-all shadow-md shadow-sky-600/20 disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
