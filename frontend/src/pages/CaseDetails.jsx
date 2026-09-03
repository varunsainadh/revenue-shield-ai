import React, { useState, useEffect } from 'react';
import { 
  X, 
  Bot, 
  ShieldCheck, 
  AlertOctagon, 
  ExternalLink, 
  CheckCircle2, 
  Play, 
  Clock, 
  Mail, 
  MessageSquare, 
  PhoneCall,
  DollarSign
} from 'lucide-react';
import { fetchAuditLogs } from '../services/api';

export default function CaseDetails({ caseData, onClose, onAnalyze, onExecute, onApprove, onReject, onSimulatePayment }) {
  const [auditLogs, setAuditLogs] = useState([]);

  useEffect(() => {
    if (caseData && caseData.id) {
      fetchAuditLogs({ case_id: caseData.id }).then(setAuditLogs).catch(() => {});
    }
  }, [caseData]);

  if (!caseData) return null;

  let channelScores = {};
  try {
    if (caseData.channel_scores_json) {
      channelScores = JSON.parse(caseData.channel_scores_json);
    }
  } catch (e) {}

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-[#131c2e] border border-[#1e293b] rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="p-6 border-b border-[#1e293b] flex items-center justify-between sticky top-0 bg-[#131c2e] z-10">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center font-bold">
              RC
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-xl font-bold text-white font-mono">{caseData.id}</h2>
                <span className="text-xs bg-slate-800 text-slate-300 font-mono px-2 py-0.5 rounded border border-slate-700">
                  {caseData.status}
                </span>
              </div>
              <p className="text-xs text-slate-400">Transaction: {caseData.transaction_id} | Customer: {caseData.customer_id}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Top Info Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[#0b0f19] p-4 rounded-xl border border-[#1e293b]">
              <span className="text-xs text-slate-400 block mb-1">Amount at Risk</span>
              <span className="text-xl font-extrabold text-white">₹{caseData.amount.toLocaleString('en-IN')}</span>
            </div>
            <div className="bg-[#0b0f19] p-4 rounded-xl border border-[#1e293b]">
              <span className="text-xs text-slate-400 block mb-1">Failure Reason</span>
              <span className="text-sm font-semibold text-rose-400">{caseData.failure_reason}</span>
            </div>
            <div className="bg-[#0b0f19] p-4 rounded-xl border border-[#1e293b]">
              <span className="text-xs text-slate-400 block mb-1">Failure Category</span>
              <span className="text-sm font-semibold text-sky-400">{caseData.failure_category}</span>
            </div>
            <div className="bg-[#0b0f19] p-4 rounded-xl border border-[#1e293b]">
              <span className="text-xs text-slate-400 block mb-1">Customer Success Rate</span>
              <span className="text-sm font-semibold text-emerald-400">{(caseData.customer_success_rate * 100).toFixed(0)}%</span>
            </div>
          </div>

          {/* ERV Comparison Visualization */}
          {Object.keys(channelScores).length > 0 && (
            <div className="bg-[#0b0f19] p-6 rounded-xl border border-[#1e293b]">
              <h3 className="text-sm font-bold text-white mb-4 flex items-center space-x-2">
                <DollarSign className="w-4 h-4 text-emerald-400" />
                <span>ML Channel Probability & Expected Recovery Value (ERV)</span>
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Email */}
                <div className={`p-4 rounded-xl border ${caseData.recommended_channel === 'EMAIL' ? 'border-sky-500 bg-sky-500/10' : 'border-[#1e293b] bg-[#131c2e]'}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-slate-300 flex items-center"><Mail className="w-3.5 h-3.5 mr-1" /> EMAIL</span>
                    {caseData.recommended_channel === 'EMAIL' && <span className="text-[10px] bg-sky-500 text-white font-bold px-1.5 py-0.5 rounded">RECOMMENDED</span>}
                  </div>
                  <div className="text-lg font-bold text-white">{(channelScores.email.probability * 100).toFixed(0)}% <span className="text-xs text-slate-400 font-normal">probability</span></div>
                  <div className="text-sm font-semibold text-emerald-400 mt-1">ERV: ₹{channelScores.email.erv.toLocaleString('en-IN')}</div>
                </div>

                {/* WhatsApp */}
                <div className={`p-4 rounded-xl border ${caseData.recommended_channel === 'WHATSAPP' ? 'border-emerald-500 bg-emerald-500/10' : 'border-[#1e293b] bg-[#131c2e]'}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-slate-300 flex items-center"><MessageSquare className="w-3.5 h-3.5 mr-1 text-emerald-400" /> WHATSAPP</span>
                    {caseData.recommended_channel === 'WHATSAPP' && <span className="text-[10px] bg-emerald-500 text-white font-bold px-1.5 py-0.5 rounded">RECOMMENDED</span>}
                  </div>
                  <div className="text-lg font-bold text-white">{(channelScores.whatsapp.probability * 100).toFixed(0)}% <span className="text-xs text-slate-400 font-normal">probability</span></div>
                  <div className="text-sm font-semibold text-emerald-400 mt-1">ERV: ₹{channelScores.whatsapp.erv.toLocaleString('en-IN')}</div>
                </div>

                {/* Voice */}
                <div className={`p-4 rounded-xl border ${caseData.recommended_channel === 'VOICE' ? 'border-purple-500 bg-purple-500/10' : 'border-[#1e293b] bg-[#131c2e]'}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-slate-300 flex items-center"><PhoneCall className="w-3.5 h-3.5 mr-1 text-purple-400" /> VOICE</span>
                    {caseData.recommended_channel === 'VOICE' && <span className="text-[10px] bg-purple-500 text-white font-bold px-1.5 py-0.5 rounded">RECOMMENDED</span>}
                  </div>
                  <div className="text-lg font-bold text-white">{(channelScores.voice.probability * 100).toFixed(0)}% <span className="text-xs text-slate-400 font-normal">probability</span></div>
                  <div className="text-sm font-semibold text-emerald-400 mt-1">ERV: ₹{channelScores.voice.erv.toLocaleString('en-IN')}</div>
                </div>
              </div>
            </div>
          )}

          {/* Reasoning & Policy Result */}
          {caseData.ai_reasoning && (
            <div className="bg-[#0b0f19] p-5 rounded-xl border border-[#1e293b] space-y-3">
              <div className="flex items-start space-x-3">
                <Bot className="w-5 h-5 text-sky-400 mt-0.5" />
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">AI Recommendation & Contextual Reasoning</h4>
                  <p className="text-sm text-slate-200 mt-1">{caseData.ai_reasoning}</p>
                </div>
              </div>

              {caseData.policy_reason && (
                <div className="flex items-start space-x-3 pt-3 border-t border-[#1e293b]">
                  <ShieldCheck className="w-5 h-5 text-emerald-400 mt-0.5" />
                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Policy Engine Decision</h4>
                    <p className="text-sm text-emerald-300 mt-1">{caseData.policy_reason}</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Action Bar */}
          <div className="bg-[#0b0f19] p-4 rounded-xl border border-[#1e293b] flex items-center justify-between">
            <div className="text-xs text-slate-400">
              Attempts: <span className="font-bold text-white">{caseData.attempt_number} / {caseData.max_attempts}</span>
            </div>

            <div className="flex items-center space-x-3">
              {caseData.status === 'OPEN' && (
                <button
                  onClick={() => onAnalyze(caseData.id)}
                  className="bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold px-4 py-2 rounded-lg transition-colors"
                >
                  Run RevenueShield Agent
                </button>
              )}

              {caseData.status === 'ACTION_READY' && (
                <button
                  onClick={() => onExecute(caseData.id)}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-4 py-2 rounded-lg transition-colors"
                >
                  Execute Recovery Action
                </button>
              )}

              {caseData.status === 'MANUAL_REVIEW' && (
                <>
                  <button
                    onClick={() => onApprove(caseData.id)}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-4 py-2 rounded-lg transition-colors"
                  >
                    Approve Action
                  </button>
                  <button
                    onClick={() => onReject(caseData.id)}
                    className="bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold px-4 py-2 rounded-lg transition-colors"
                  >
                    Reject Action
                  </button>
                </>
              )}

              {['WAITING_PAYMENT', 'ACTION_READY', 'PENDING_RECOVERY'].includes(caseData.status) && (
                <a
                  href={`/demo/pay/${caseData.id}`}
                  target="_blank"
                  rel="noreferrer"
                  className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-4 py-2 rounded-lg transition-colors flex items-center space-x-1"
                >
                  <span>Open Demo Checkout Page</span>
                  <ExternalLink className="w-3.5 h-3.5 ml-1" />
                </a>
              )}
            </div>
          </div>

          {/* Audit Trail Timeline for Case */}
          <div>
            <h3 className="text-sm font-bold text-white mb-3">Case Audit Timeline</h3>
            <div className="space-y-2.5">
              {auditLogs.map((log) => (
                <div key={log.id} className="bg-[#0b0f19] p-3 rounded-lg border border-[#1e293b] flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-3">
                    <span className="text-slate-500 font-mono">{new Date(log.timestamp).toLocaleTimeString()}</span>
                    <span className="font-semibold text-slate-300">{log.action}</span>
                  </div>
                  <span className="bg-slate-800 text-slate-400 font-mono px-2 py-0.5 rounded text-[10px]">{log.event_type}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
