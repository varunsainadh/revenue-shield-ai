import React from 'react';
import { 
  DollarSign, 
  TrendingUp, 
  Percent, 
  Activity, 
  ArrowUpRight, 
  Play, 
  CheckCircle2, 
  AlertTriangle,
  RefreshCw
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, Cell 
} from 'recharts';

export default function Overview({ analytics, onSelectCase, onSeedData, loading }) {
  if (!analytics || !analytics.metrics) {
    return (
      <div className="p-8 text-center text-slate-400">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-sky-400" />
        Loading RevenueShield Analytics...
      </div>
    );
  }

  const { metrics, revenue_trend, funnel, channel_performance, failure_reasons } = analytics;

  const CHANNEL_COLORS = {
    WHATSAPP: '#10b981',
    EMAIL: '#3b82f6',
    VOICE: '#8b5cf6'
  };

  return (
    <div className="p-8 space-y-8">
      {/* Header Banner */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">RevenueShield AI</h1>
          <p className="text-sm text-slate-400">AI-powered recovery for revenue at risk.</p>
        </div>
        <button
          onClick={onSeedData}
          disabled={loading}
          className="flex items-center space-x-2 bg-sky-600 hover:bg-sky-500 text-white font-medium px-4 py-2 rounded-lg text-sm transition-all shadow-md shadow-sky-600/20"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Seed Synthetic Demo Data</span>
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="bg-[#131c2e] border border-[#1e293b] rounded-xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Revenue At Risk</span>
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-white">₹{metrics.revenue_at_risk.toLocaleString('en-IN')}</div>
          <div className="mt-2 flex items-center text-xs text-slate-400">
            <span>From {metrics.total_transactions} failed transactions</span>
          </div>
        </div>

        <div className="bg-[#131c2e] border border-[#1e293b] rounded-xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Recovered Revenue</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-emerald-400">₹{metrics.recovered_revenue.toLocaleString('en-IN')}</div>
          <div className="mt-2 flex items-center text-xs text-emerald-400">
            <ArrowUpRight className="w-3.5 h-3.5 mr-1" />
            <span>Net ERV: ₹{metrics.net_recovered_revenue.toLocaleString('en-IN')}</span>
          </div>
        </div>

        <div className="bg-[#131c2e] border border-[#1e293b] rounded-xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Recovery Rate</span>
            <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
              <Percent className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-sky-400">{metrics.recovery_rate}%</div>
          <div className="mt-2 flex items-center text-xs text-slate-400">
            <span>Efficiency: {metrics.recovery_efficiency}%</span>
          </div>
        </div>

        <div className="bg-[#131c2e] border border-[#1e293b] rounded-xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Active Recovery Cases</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-white">{metrics.active_recovery_cases}</div>
          <div className="mt-2 flex items-center text-xs text-amber-400">
            <AlertTriangle className="w-3.5 h-3.5 mr-1" />
            <span>{metrics.manual_reviews} Manual Reviews Pending</span>
          </div>
        </div>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart */}
        <div className="lg:col-span-2 bg-[#131c2e] border border-[#1e293b] rounded-xl p-6">
          <h2 className="text-base font-bold text-white mb-4">Recovered Revenue vs Revenue At Risk</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={revenue_trend}>
                <defs>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorRec" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `₹${v/1000}k`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0b0f19', borderColor: '#1e293b', borderRadius: '8px', color: '#fff' }} 
                  formatter={(val) => [`₹${val.toLocaleString('en-IN')}`, '']}
                />
                <Area type="monotone" dataKey="at_risk" name="Revenue At Risk" stroke="#f43f5e" fillOpacity={1} fill="url(#colorRisk)" />
                <Area type="monotone" dataKey="recovered" name="Recovered Revenue" stroke="#10b981" fillOpacity={1} fill="url(#colorRec)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Channel Performance Breakdown */}
        <div className="bg-[#131c2e] border border-[#1e293b] rounded-xl p-6">
          <h2 className="text-base font-bold text-white mb-4">Top Channel Performance</h2>
          <div className="space-y-4">
            {channel_performance.map((ch, idx) => (
              <div key={idx} className="bg-[#0b0f19] p-4 rounded-lg border border-[#1e293b]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-white">{ch.channel}</span>
                  <span className="text-xs font-mono text-emerald-400">₹{ch.recovered_amount.toLocaleString('en-IN')}</span>
                </div>
                <div className="w-full bg-[#1e293b] h-2 rounded-full overflow-hidden">
                  <div 
                    className="h-full rounded-full" 
                    style={{ 
                      width: `${Math.min(100, (ch.recovered_amount / (metrics.recovered_revenue || 1)) * 100)}%`,
                      backgroundColor: CHANNEL_COLORS[ch.channel] || '#38bdf8'
                    }}
                  ></div>
                </div>
                <div className="mt-2 text-xs text-slate-400 text-right">
                  {ch.recoveries} successful recoveries
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recovery Funnel */}
      <div className="bg-[#131c2e] border border-[#1e293b] rounded-xl p-6">
        <h2 className="text-base font-bold text-white mb-4">AI Recovery Funnel</h2>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          {funnel.map((step, idx) => (
            <div key={idx} className="bg-[#0b0f19] p-3.5 rounded-lg border border-[#1e293b] text-center relative">
              <div className="text-[11px] text-slate-400 font-medium">{step.stage}</div>
              <div className="text-lg font-bold text-white my-1">{step.count}</div>
              <div className="text-[10px] text-sky-400 font-mono bg-sky-500/10 py-0.5 px-1.5 rounded inline-block">
                {step.conversion}%
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
