import React from 'react';
import { ShieldAlert, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

export default function ManualReview({ manualCases, onApprove, onReject, onStop }) {
  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Manual Review Queue</h1>
          <p className="text-sm text-slate-400">High-value transactions and restricted policy interventions requiring merchant approval.</p>
        </div>
      </div>

      {manualCases.length === 0 ? (
        <div className="bg-[#131c2e] border border-[#1e293b] rounded-xl p-12 text-center text-slate-400">
          <ShieldAlert className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-white">Manual Review Queue Clean</h3>
          <p className="text-xs text-slate-400 mt-1">No pending cases require manual human intervention.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {manualCases.map((c) => (
            <div key={c.id} className="bg-[#131c2e] border border-amber-500/30 rounded-xl p-6 space-y-4 relative shadow-lg">
              <div className="flex items-center justify-between">
                <span className="font-mono text-sm font-bold text-amber-400">{c.id}</span>
                <span className="text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2.5 py-1 rounded-full">
                  HIGH VALUE REVIEW
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 bg-[#0b0f19] p-3.5 rounded-lg text-xs">
                <div>
                  <span className="text-slate-400 block">Amount</span>
                  <span className="text-base font-bold text-white">₹{c.amount.toLocaleString('en-IN')}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">Failure Reason</span>
                  <span className="font-semibold text-rose-400">{c.failure_reason}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">Rec. Channel</span>
                  <span className="font-semibold text-sky-400">{c.recommended_channel || 'WHATSAPP'}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">ERV</span>
                  <span className="font-semibold text-emerald-400">₹{c.recommended_erv ? c.recommended_erv.toLocaleString('en-IN') : '-'}</span>
                </div>
              </div>

              <div className="bg-amber-500/10 border border-amber-500/20 p-3 rounded-lg text-xs text-amber-300">
                <AlertTriangle className="w-4 h-4 text-amber-400 inline mr-1.5 -mt-0.5" />
                {c.policy_reason || "Transaction amount exceeds auto-approval threshold (₹15,000). Manual review required."}
              </div>

              <div className="flex items-center space-x-3 pt-2">
                <button
                  onClick={() => onApprove(c.id)}
                  className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 rounded-lg text-xs transition-colors shadow-md shadow-emerald-600/20 flex items-center justify-center space-x-1"
                >
                  <CheckCircle className="w-4 h-4 mr-1" />
                  <span>APPROVE & RECOVER</span>
                </button>
                <button
                  onClick={() => onReject(c.id)}
                  className="flex-1 bg-rose-600 hover:bg-rose-500 text-white font-bold py-2 rounded-lg text-xs transition-colors flex items-center justify-center space-x-1"
                >
                  <XCircle className="w-4 h-4 mr-1" />
                  <span>REJECT INTERVENTION</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
