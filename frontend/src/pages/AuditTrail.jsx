import React, { useState } from 'react';
import { History, Filter, Search, Terminal } from 'lucide-react';

export default function AuditTrail({ auditLogs }) {
  const [filterType, setFilterType] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredLogs = auditLogs.filter(log => {
    const matchesSearch = !searchTerm || (log.action && log.action.toLowerCase().includes(searchTerm.toLowerCase())) || (log.case_id && log.case_id.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = !filterType || log.event_type === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Audit Trail & Compliance Log</h1>
          <p className="text-sm text-slate-400">Deterministic immutable log of every agent score, policy check, and financial action.</p>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-[#131c2e] border border-[#1e293b] rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Filter audit events by action or case ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#0b0f19] border border-[#1e293b] text-sm text-slate-200 pl-10 pr-4 py-2 rounded-lg focus:outline-none focus:border-sky-500"
          />
        </div>

        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="bg-[#0b0f19] border border-[#1e293b] text-sm text-slate-200 px-3 py-2 rounded-lg focus:outline-none focus:border-sky-500"
        >
          <option value="">All Event Types</option>
          <option value="CASE_CREATED">CASE_CREATED</option>
          <option value="ML_SCORE_GENERATED">ML_SCORE_GENERATED</option>
          <option value="ERV_CALCULATED">ERV_CALCULATED</option>
          <option value="POLICY_ALLOWED">POLICY_ALLOWED</option>
          <option value="REVENUE_RECOVERED">REVENUE_RECOVERED</option>
          <option value="MANUAL_APPROVED">MANUAL_APPROVED</option>
        </select>
      </div>

      {/* Log Timeline */}
      <div className="bg-[#131c2e] border border-[#1e293b] rounded-xl p-6 shadow-xl">
        <div className="space-y-4">
          {filteredLogs.map((log) => (
            <div key={log.id} className="bg-[#0b0f19] p-4 rounded-xl border border-[#1e293b] flex items-start justify-between space-x-4">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded border border-sky-500/20 font-bold">
                    {log.event_type}
                  </span>
                  {log.case_id && (
                    <span className="text-xs font-mono text-slate-400">
                      Case: <strong className="text-white">{log.case_id}</strong>
                    </span>
                  )}
                </div>
                <p className="text-sm font-semibold text-slate-200">{log.action}</p>
                {log.reason && <p className="text-xs text-slate-400 italic">{log.reason}</p>}
              </div>

              <div className="text-right flex-shrink-0">
                <span className="text-xs font-mono text-slate-500 block">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span className="text-[10px] text-slate-400 uppercase font-mono">{log.actor}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
