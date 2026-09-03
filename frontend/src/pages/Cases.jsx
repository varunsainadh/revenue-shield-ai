import React, { useState } from 'react';
import { Search, Filter, Play, CheckCircle, Clock, AlertTriangle, ArrowUpRight, Eye } from 'lucide-react';

export default function Cases({ cases, onSelectCase, onAnalyzeCase, onExecuteRecovery }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [channelFilter, setChannelFilter] = useState('');

  const filteredCases = cases.filter(c => {
    const matchesSearch = c.id.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          c.customer_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          c.transaction_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter ? c.status === statusFilter : true;
    const matchesChannel = channelFilter ? c.recommended_channel === channelFilter : true;
    return matchesSearch && matchesStatus && matchesChannel;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'RECOVERED':
        return <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2.5 py-1 rounded-full text-xs font-semibold">RECOVERED</span>;
      case 'MANUAL_REVIEW':
        return <span className="bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2.5 py-1 rounded-full text-xs font-semibold">MANUAL REVIEW</span>;
      case 'WAITING_PAYMENT':
        return <span className="bg-sky-500/10 text-sky-400 border border-sky-500/30 px-2.5 py-1 rounded-full text-xs font-semibold">WAITING PAYMENT</span>;
      case 'ACTION_READY':
        return <span className="bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 px-2.5 py-1 rounded-full text-xs font-semibold font-mono">ACTION READY</span>;
      case 'STOPPED':
        return <span className="bg-rose-500/10 text-rose-400 border border-rose-500/30 px-2.5 py-1 rounded-full text-xs font-semibold">STOPPED</span>;
      default:
        return <span className="bg-slate-800 text-slate-300 border border-slate-700 px-2.5 py-1 rounded-full text-xs font-semibold">{status}</span>;
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Recovery Cases</h1>
          <p className="text-sm text-slate-400">Manage and execute autonomous recovery workflows for failed payments.</p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-[#131c2e] border border-[#1e293b] rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search Case ID, Customer ID, Transaction..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#0b0f19] border border-[#1e293b] text-sm text-slate-200 pl-10 pr-4 py-2 rounded-lg focus:outline-none focus:border-sky-500"
          />
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#0b0f19] border border-[#1e293b] text-sm text-slate-200 px-3 py-2 rounded-lg focus:outline-none focus:border-sky-500"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">OPEN</option>
            <option value="ACTION_READY">ACTION_READY</option>
            <option value="WAITING_PAYMENT">WAITING_PAYMENT</option>
            <option value="MANUAL_REVIEW">MANUAL_REVIEW</option>
            <option value="RECOVERED">RECOVERED</option>
            <option value="STOPPED">STOPPED</option>
          </select>

          <select
            value={channelFilter}
            onChange={(e) => setChannelFilter(e.target.value)}
            className="bg-[#0b0f19] border border-[#1e293b] text-sm text-slate-200 px-3 py-2 rounded-lg focus:outline-none focus:border-sky-500"
          >
            <option value="">All Channels</option>
            <option value="WHATSAPP">WHATSAPP</option>
            <option value="EMAIL">EMAIL</option>
            <option value="VOICE">VOICE</option>
          </select>
        </div>
      </div>

      {/* Cases Table */}
      <div className="bg-[#131c2e] border border-[#1e293b] rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-[#0b0f19] text-xs font-semibold text-slate-400 uppercase tracking-wider border-b border-[#1e293b]">
              <tr>
                <th className="p-4">Case ID</th>
                <th className="p-4">Customer</th>
                <th className="p-4">Amount</th>
                <th className="p-4">Failure Reason</th>
                <th className="p-4">Rec. Channel</th>
                <th className="p-4">ERV</th>
                <th className="p-4">Status</th>
                <th className="p-4 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e293b]">
              {filteredCases.map((c) => (
                <tr key={c.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-4 font-mono font-semibold text-sky-400">{c.id}</td>
                  <td className="p-4">{c.customer_id}</td>
                  <td className="p-4 font-bold text-white">₹{c.amount.toLocaleString('en-IN')}</td>
                  <td className="p-4">
                    <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded text-xs">
                      {c.failure_reason}
                    </span>
                  </td>
                  <td className="p-4">
                    {c.recommended_channel ? (
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                        c.recommended_channel === 'WHATSAPP' ? 'bg-emerald-500/20 text-emerald-400' :
                        c.recommended_channel === 'EMAIL' ? 'bg-blue-500/20 text-blue-400' : 'bg-purple-500/20 text-purple-400'
                      }`}>
                        {c.recommended_channel}
                      </span>
                    ) : (
                      <span className="text-slate-500 text-xs">Unanalyzed</span>
                    )}
                  </td>
                  <td className="p-4 font-mono text-emerald-400 font-semibold">
                    {c.recommended_erv ? `₹${c.recommended_erv.toLocaleString('en-IN')}` : '-'}
                  </td>
                  <td className="p-4">{getStatusBadge(c.status)}</td>
                  <td className="p-4 text-center space-x-2">
                    <button
                      onClick={() => onSelectCase(c)}
                      className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
                      title="View Details"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    {c.status === 'OPEN' && (
                      <button
                        onClick={() => onAnalyzeCase(c.id)}
                        className="px-2.5 py-1 rounded bg-sky-600 hover:bg-sky-500 text-white font-medium text-xs transition-colors"
                      >
                        Analyze
                      </button>
                    )}
                    {c.status === 'ACTION_READY' && (
                      <button
                        onClick={() => onExecuteRecovery(c.id)}
                        className="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs transition-colors"
                      >
                        Recover
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
