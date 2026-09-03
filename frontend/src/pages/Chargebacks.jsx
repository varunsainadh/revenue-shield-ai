import React, { useState, useEffect } from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle2, Zap, RefreshCw, Layers } from 'lucide-react';
import { fetchChargebacks, predictChargeback } from '../services/api';

export default function Chargebacks() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadPredictions();
  }, []);

  const loadPredictions = async () => {
    try {
      setLoading(true);
      const data = await fetchChargebacks();
      setPredictions(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handlePredictOnDemand = async () => {
    setLoading(true);
    await predictChargeback({
      transaction_id: `tx_cb_demand_${Date.now()}`,
      customer_id: `cust_${Math.floor(1000 + Math.random() * 9000)}`,
      amount: 19500.0,
      payment_method: 'UPI',
      previous_failure_count: 2,
      is_first_time_customer: true,
      failure_reason: 'fraud_suspected'
    });
    await loadPredictions();
    setLoading(false);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-rose-500 border-rose-500/30 bg-rose-500/10';
    if (score >= 60) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    if (score >= 35) return 'text-sky-400 border-sky-500/30 bg-sky-500/10';
    return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">AI Chargeback Risk Predictor</h1>
          <p className="text-sm text-slate-400">Pre-dispute machine learning prediction and Explainable AI (XAI) risk factor attribution.</p>
        </div>

        <button
          onClick={handlePredictOnDemand}
          disabled={loading}
          className="bg-sky-600 hover:bg-sky-500 text-white font-bold px-4 py-2 rounded-lg text-xs transition-all shadow-md shadow-sky-600/20 flex items-center space-x-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Run On-Demand Chargeback Assessment</span>
        </button>
      </div>

      {/* Chargebacks Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {predictions.map((pred) => {
          let factors = [];
          try {
            factors = JSON.parse(pred.top_risk_factors_json);
          } catch (e) {}

          return (
            <div key={pred.id} className="bg-[#131c2e] border border-[#1e293b] rounded-2xl p-6 space-y-4 shadow-xl relative overflow-hidden">
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-mono text-sm font-bold text-sky-400">{pred.transaction_id}</span>
                  <p className="text-xs text-slate-400">Customer: {pred.customer_id}</p>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-bold border ${getScoreColor(pred.risk_score)}`}>
                  Risk Score: {pred.risk_score}% ({pred.risk_level})
                </div>
              </div>

              {/* Amount Display */}
              <div className="bg-[#0b0f19] p-4 rounded-xl border border-[#1e293b] flex items-center justify-between">
                <div>
                  <span className="text-xs text-slate-400 block">Transaction Amount</span>
                  <span className="text-xl font-extrabold text-white">₹{pred.amount.toLocaleString('en-IN')}</span>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-400 block">ML Model Confidence</span>
                  <span className="text-sm font-semibold text-emerald-400">{(pred.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>

              {/* XAI Factors Attribution */}
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center">
                  <Layers className="w-3.5 h-3.5 mr-1 text-sky-400" /> Explainable AI (XAI) Contributing Factors
                </h4>
                <div className="space-y-2">
                  {factors.map((f, idx) => (
                    <div key={idx} className="bg-[#0b0f19] p-3 rounded-lg border border-[#1e293b] text-xs">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-slate-200">{f.factor}</span>
                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                          f.impact === 'HIGH' ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'
                        }`}>
                          {f.impact} IMPACT
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400">{f.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Summary Explanation */}
              <div className="p-3 bg-sky-500/10 border border-sky-500/20 rounded-xl text-xs text-sky-300">
                <span className="font-bold">AI Rationale: </span>{pred.explanation}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
