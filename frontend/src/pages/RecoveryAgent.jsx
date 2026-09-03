import React, { useState } from 'react';
import { Bot, ShieldCheck, CheckCircle2, Play, ArrowRight, Zap, RefreshCw } from 'lucide-react';

export default function RecoveryAgent({ cases, onAnalyzeCase, onExecuteRecovery }) {
  const [selectedCaseId, setSelectedCaseId] = useState(cases.length > 0 ? cases[0].id : '');
  const activeCase = cases.find(c => c.id === selectedCaseId) || cases[0];

  const pipelineStages = [
    { id: 'DETECTED', label: 'Payment Failed', desc: 'Failure event ingested' },
    { id: 'CLASSIFIED', label: 'Root Cause Classified', desc: activeCase ? activeCase.failure_category : 'Category mapping' },
    { id: 'SCORED', label: 'ML Channel Scored', desc: 'Email / WA / Voice probabilities' },
    { id: 'RECOMMENDATION', label: 'AI Recommendation', desc: activeCase ? `${activeCase.recommended_channel || 'WHATSAPP'} suggested` : 'Highest ERV candidate' },
    { id: 'POLICY_CHECK', label: 'Policy Engine Check', desc: activeCase ? (activeCase.policy_result || 'ALLOW') : 'Guardrail validation' },
    { id: 'EXECUTION', label: 'Action Executed', desc: 'Payment link generated' },
    { id: 'WAITING', label: 'Waiting Payment', desc: 'Customer engaged' },
    { id: 'RECOVERED', label: 'Revenue Recovered', desc: 'Webhook confirmed' }
  ];

  return (
    <div className="p-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Recovery Agent Pipeline</h1>
          <p className="text-sm text-slate-400">Autonomous AI decisioning and policy guardrail execution engine.</p>
        </div>
      </div>

      {/* Case Selector Dropdown */}
      <div className="bg-[#131c2e] border border-[#1e293b] rounded-xl p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Bot className="w-5 h-5 text-sky-400" />
          <span className="text-sm font-semibold text-slate-200">Select Active Case:</span>
          <select
            value={selectedCaseId}
            onChange={(e) => setSelectedCaseId(e.target.value)}
            className="bg-[#0b0f19] border border-[#1e293b] text-sm text-white px-3 py-1.5 rounded-lg font-mono focus:outline-none focus:border-sky-500"
          >
            {cases.map((c) => (
              <option key={c.id} value={c.id}>
                {c.id} — ₹{c.amount} ({c.failure_reason})
              </option>
            ))}
          </select>
        </div>

        {activeCase && (
          <div className="flex items-center space-x-2">
            {activeCase.status === 'OPEN' && (
              <button
                onClick={() => onAnalyzeCase(activeCase.id)}
                className="bg-sky-600 hover:bg-sky-500 text-white font-bold px-4 py-2 rounded-lg text-xs transition-all shadow-md shadow-sky-600/20"
              >
                Run Agent Analysis
              </button>
            )}
            {activeCase.status === 'ACTION_READY' && (
              <button
                onClick={() => onExecuteRecovery(activeCase.id)}
                className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-4 py-2 rounded-lg text-xs transition-all shadow-md shadow-emerald-600/20"
              >
                Execute Recovery
              </button>
            )}
          </div>
        )}
      </div>

      {/* Visual Pipeline Flow */}
      {activeCase && (
        <div className="bg-[#131c2e] border border-[#1e293b] rounded-2xl p-6 space-y-6">
          <h2 className="text-base font-bold text-white">Live Decisioning Pipeline for Case <span className="font-mono text-sky-400">{activeCase.id}</span></h2>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {pipelineStages.map((stage, idx) => (
              <div 
                key={stage.id}
                className={`p-4 rounded-xl border transition-all ${
                  idx < 4 
                    ? 'border-sky-500/30 bg-sky-500/5' 
                    : idx < 6 
                    ? 'border-emerald-500/30 bg-emerald-500/5' 
                    : 'border-[#1e293b] bg-[#0b0f19]'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono text-slate-500 font-bold uppercase">STEP 0{idx + 1}</span>
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                </div>
                <h3 className="text-xs font-bold text-white">{stage.label}</h3>
                <p className="text-[11px] text-slate-400 mt-1">{stage.desc}</p>
              </div>
            ))}
          </div>

          {/* Reasoning Summary Card */}
          <div className="bg-[#0b0f19] p-5 rounded-xl border border-[#1e293b] space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center space-x-2">
              <Zap className="w-4 h-4 text-amber-400" />
              <span>Agent Strategic Rationale Summary</span>
            </h3>
            <p className="text-sm text-slate-200 leading-relaxed font-sans">
              {activeCase.ai_reasoning || "WhatsApp was selected because this customer's past WhatsApp recovery behavior and the current failure type produced the highest expected recovery value."}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
