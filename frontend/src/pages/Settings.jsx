import React, { useState } from 'react';
import { Settings as SettingsIcon, Save, CheckCircle2 } from 'lucide-react';

export default function Settings({ settingsData, onSaveSettings }) {
  const [formData, setFormData] = useState(settingsData || {
    auto_recovery_enabled: true,
    max_attempts: 3,
    recovery_window_hours: 72,
    high_value_threshold: 15000.0,
    quiet_hours_start: 21,
    quiet_hours_end: 9,
    voice_enabled: true,
    whatsapp_enabled: true,
    email_enabled: true,
    merchant_timezone: 'Asia/Kolkata'
  });

  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSaveSettings(formData);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="p-8 space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Merchant Operational Settings</h1>
        <p className="text-sm text-slate-400">Configure financial thresholds, quiet hours, and channel enablement policies.</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-[#131c2e] border border-[#1e293b] rounded-xl p-6 space-y-6">
        {/* General Options */}
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider text-sky-400">Financial Guardrails</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1.5">High-Value Threshold (₹)</label>
              <input
                type="number"
                value={formData.high_value_threshold}
                onChange={(e) => setFormData({ ...formData, high_value_threshold: parseFloat(e.target.value) })}
                className="w-full bg-[#0b0f19] border border-[#1e293b] text-sm text-white px-3 py-2 rounded-lg focus:outline-none focus:border-sky-500 font-mono"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1.5">Maximum Recovery Attempts</label>
              <input
                type="number"
                value={formData.max_attempts}
                onChange={(e) => setFormData({ ...formData, max_attempts: parseInt(e.target.value) })}
                className="w-full bg-[#0b0f19] border border-[#1e293b] text-sm text-white px-3 py-2 rounded-lg focus:outline-none focus:border-sky-500 font-mono"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1.5">Recovery Window (Hours)</label>
              <input
                type="number"
                value={formData.recovery_window_hours}
                onChange={(e) => setFormData({ ...formData, recovery_window_hours: parseInt(e.target.value) })}
                className="w-full bg-[#0b0f19] border border-[#1e293b] text-sm text-white px-3 py-2 rounded-lg focus:outline-none focus:border-sky-500 font-mono"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1.5">Merchant Timezone</label>
              <input
                type="text"
                value={formData.merchant_timezone}
                onChange={(e) => setFormData({ ...formData, merchant_timezone: e.target.value })}
                className="w-full bg-[#0b0f19] border border-[#1e293b] text-sm text-white px-3 py-2 rounded-lg focus:outline-none focus:border-sky-500"
              />
            </div>
          </div>
        </div>

        {/* Quiet Hours */}
        <div className="pt-4 border-t border-[#1e293b] space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider text-sky-400">Quiet Hours Compliance</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1.5">Quiet Hours Start (Hour 0-23)</label>
              <input
                type="number"
                value={formData.quiet_hours_start}
                onChange={(e) => setFormData({ ...formData, quiet_hours_start: parseInt(e.target.value) })}
                className="w-full bg-[#0b0f19] border border-[#1e293b] text-sm text-white px-3 py-2 rounded-lg focus:outline-none focus:border-sky-500 font-mono"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1.5">Quiet Hours End (Hour 0-23)</label>
              <input
                type="number"
                value={formData.quiet_hours_end}
                onChange={(e) => setFormData({ ...formData, quiet_hours_end: parseInt(e.target.value) })}
                className="w-full bg-[#0b0f19] border border-[#1e293b] text-sm text-white px-3 py-2 rounded-lg focus:outline-none focus:border-sky-500 font-mono"
              />
            </div>
          </div>
        </div>

        {/* Channel Enablement Toggles */}
        <div className="pt-4 border-t border-[#1e293b] space-y-3">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider text-sky-400">Channel Control</h2>

          <div className="space-y-2">
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.whatsapp_enabled}
                onChange={(e) => setFormData({ ...formData, whatsapp_enabled: e.target.checked })}
                className="w-4 h-4 rounded text-sky-500 bg-[#0b0f19] border-[#1e293b]"
              />
              <span className="text-sm text-slate-200">WhatsApp Recovery Channel Enabled</span>
            </label>

            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.email_enabled}
                onChange={(e) => setFormData({ ...formData, email_enabled: e.target.checked })}
                className="w-4 h-4 rounded text-sky-500 bg-[#0b0f19] border-[#1e293b]"
              />
              <span className="text-sm text-slate-200">Email Recovery Channel Enabled</span>
            </label>

            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.voice_enabled}
                onChange={(e) => setFormData({ ...formData, voice_enabled: e.target.checked })}
                className="w-4 h-4 rounded text-sky-500 bg-[#0b0f19] border-[#1e293b]"
              />
              <span className="text-sm text-slate-200">Voice Recovery Channel Enabled</span>
            </label>
          </div>
        </div>

        <div className="pt-4 flex items-center justify-between">
          {savedSuccess ? (
            <span className="text-xs text-emerald-400 font-semibold flex items-center">
              <CheckCircle2 className="w-4 h-4 mr-1" /> Settings updated successfully!
            </span>
          ) : <span></span>}

          <button
            type="submit"
            className="bg-sky-600 hover:bg-sky-500 text-white font-bold px-6 py-2.5 rounded-lg text-sm transition-all shadow-md shadow-sky-600/20 flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Save Configuration</span>
          </button>
        </div>
      </form>
    </div>
  );
}
