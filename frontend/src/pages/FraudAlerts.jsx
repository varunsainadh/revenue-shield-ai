import React, { useState, useEffect } from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { fetchFraudAlerts, resolveFraudAlert } from '../services/api';

export default function FraudAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const data = await fetchFraudAlerts();
      setAlerts(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async (id, status) => {
    setLoading(true);
    await resolveFraudAlert(id, status, "Investigated and updated by merchant operator");
    await loadAlerts();
    setLoading(false);
  };

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return <span className="bg-rose-500/20 text-rose-400 border border-rose-500/30 px-2.5 py-1 rounded-full text-xs font-bold">CRITICAL SEVERITY</span>;
      case 'HIGH':
        return <span className="bg-amber-500/20 text-amber-400 border border-amber-500/30 px-2.5 py-1 rounded-full text-xs font-bold">HIGH SEVERITY</span>;
      default:
        return <span className="bg-sky-500/20 text-sky-400 border border-sky-500/30 px-2.5 py-1 rounded-full text-xs font-bold">{severity}</span>;
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Fraud & Anomaly Detection Center</h1>
          <p className="text-sm text-slate-400">Real-time alerts for refund abuse, duplicate refunds, and velocity spikes.</p>
        </div>

        <button
          onClick={loadAlerts}
          disabled={loading}
          className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold px-4 py-2 rounded-lg text-xs transition-colors flex items-center space-x-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Alerts</span>
        </button>
      </div>

      {/* Alerts Stream */}
      <div className="space-y-4">
        {alerts.map((alert) => (
          <div key={alert.id} className="bg-[#131c2e] border border-[#1e293b] rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl">
            <div className="space-y-2 flex-1">
              <div className="flex items-center space-x-3">
                <span className="text-xs font-mono bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700 font-bold">
                  {alert.alert_type}
                </span>
                {getSeverityBadge(alert.severity)}
                <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                  alert.status === 'OPEN' ? 'bg-amber-500/10 text-amber-400' : 'bg-emerald-500/10 text-emerald-400'
                }`}>
                  {alert.status}
                </span>
              </div>

              <h3 className="text-base font-bold text-white">{alert.description}</h3>
              <p className="text-xs text-slate-400 font-mono">
                Transaction: {alert.transaction_id || 'System Wide'} | Customer: {alert.customer_id || 'N/A'} | Time: {new Date(alert.created_at).toLocaleString()}
              </p>
            </div>

            {alert.status === 'OPEN' && (
              <div className="flex items-center space-x-2 flex-shrink-0">
                <button
                  onClick={() => handleResolve(alert.id, 'RESOLVED')}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-3.5 py-2 rounded-lg text-xs transition-colors flex items-center space-x-1"
                >
                  <CheckCircle className="w-4 h-4 mr-1" />
                  <span>RESOLVE</span>
                </button>
                <button
                  onClick={() => handleResolve(alert.id, 'DISMISSED')}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold px-3.5 py-2 rounded-lg text-xs transition-colors flex items-center space-x-1"
                >
                  <XCircle className="w-4 h-4 mr-1" />
                  <span>DISMISS</span>
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
