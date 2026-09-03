import React from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell 
} from 'recharts';

export default function Analytics({ analytics }) {
  if (!analytics || !analytics.metrics) return null;
  const { metrics, failure_reasons, channel_performance } = analytics;

  const COLORS = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444'];

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Recovery Performance Analytics</h1>
        <p className="text-sm text-slate-400">Deep business metrics, channel yields, and recovery efficiency breakdowns.</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#131c2e] p-4 rounded-xl border border-[#1e293b]">
          <span className="text-xs text-slate-400 block">Recovery Rate</span>
          <span className="text-xl font-bold text-emerald-400">{metrics.recovery_rate}%</span>
        </div>
        <div className="bg-[#131c2e] p-4 rounded-xl border border-[#1e293b]">
          <span className="text-xs text-slate-400 block">Recovery Efficiency</span>
          <span className="text-xl font-bold text-sky-400">{metrics.recovery_efficiency}%</span>
        </div>
        <div className="bg-[#131c2e] p-4 rounded-xl border border-[#1e293b]">
          <span className="text-xs text-slate-400 block">Manual Review Rate</span>
          <span className="text-xl font-bold text-amber-400">
            {((metrics.manual_reviews / (metrics.total_transactions || 1)) * 100).toFixed(1)}%
          </span>
        </div>
        <div className="bg-[#131c2e] p-4 rounded-xl border border-[#1e293b]">
          <span className="text-xs text-slate-400 block">Blocked Risk Rate</span>
          <span className="text-xl font-bold text-rose-400">
            {((metrics.blocked_cases / (metrics.total_transactions || 1)) * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Failure Reasons Breakdown */}
        <div className="bg-[#131c2e] border border-[#1e293b] rounded-xl p-6">
          <h2 className="text-base font-bold text-white mb-4">Failure Reason Distribution</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={failure_reasons.slice(0, 6)}>
                <XAxis dataKey="reason" stroke="#64748b" fontSize={10} interval={0} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#0b0f19', borderColor: '#1e293b', color: '#fff' }} />
                <Bar dataKey="count" fill="#38bdf8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Channel Yield */}
        <div className="bg-[#131c2e] border border-[#1e293b] rounded-xl p-6">
          <h2 className="text-base font-bold text-white mb-4">Recovered Revenue by Channel</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={channel_performance}>
                <XAxis dataKey="channel" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `₹${v/1000}k`} />
                <Tooltip contentStyle={{ backgroundColor: '#0b0f19', borderColor: '#1e293b', color: '#fff' }} />
                <Bar dataKey="recovered_amount" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
