import React from 'react';
import { 
  LayoutDashboard, 
  FolderKanban, 
  Bot, 
  ShieldAlert, 
  History, 
  BarChart3, 
  Settings as SettingsIcon,
  Shield,
  Zap,
  Sparkles,
  AlertTriangle,
  FileText
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, appMode = 'mock', useRazorpay = false }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'copilot', label: 'AI Copilot', icon: Sparkles, badge: 'RAG' },
    { id: 'cases', label: 'Recovery Cases', icon: FolderKanban },
    { id: 'chargebacks', label: 'Chargeback Risk', icon: ShieldAlert, badge: 'XAI' },
    { id: 'fraud', label: 'Fraud & Refund Alerts', icon: AlertTriangle },
    { id: 'agent', label: 'Recovery Agent', icon: Bot },
    { id: 'review', label: 'Manual Review', icon: ShieldAlert },
    { id: 'audit', label: 'Audit Trail', icon: History },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 bg-[#131c2e] border-r border-[#1e293b] flex flex-col justify-between h-screen sticky top-0">
      <div>
        {/* Brand Header */}
        <div className="p-6 border-b border-[#1e293b] flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white tracking-tight flex items-center gap-1.5">
              RevenueShield <span className="text-xs bg-sky-500/20 text-sky-400 font-mono px-1.5 py-0.5 rounded border border-sky-500/30">AI</span>
            </h1>
            <p className="text-[11px] text-slate-400 font-medium">Detect. Decide. Recover.</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive 
                    ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20 shadow-sm' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] bg-sky-500/20 text-sky-300 font-mono font-bold px-1.5 py-0.5 rounded">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Mode Badge Footer */}
      <div className="p-4 border-t border-[#1e293b]">
        <div className="p-3 rounded-lg bg-[#0b0f19] border border-[#1e293b] flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Zap className={`w-4 h-4 ${useRazorpay ? 'text-emerald-400' : 'text-amber-400'}`} />
            <span className="text-xs font-semibold text-slate-300">
              {useRazorpay ? 'RAZORPAY TEST MODE' : 'DEMO MOCK MODE'}
            </span>
          </div>
          <span className={`w-2 h-2 rounded-full animate-pulse ${useRazorpay ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
        </div>
      </div>
    </aside>
  );
}
