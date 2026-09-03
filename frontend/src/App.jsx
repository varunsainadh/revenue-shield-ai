import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import Copilot from './pages/Copilot';
import Cases from './pages/Cases';
import Chargebacks from './pages/Chargebacks';
import FraudAlerts from './pages/FraudAlerts';
import CaseDetails from './pages/CaseDetails';
import RecoveryAgent from './pages/RecoveryAgent';
import ManualReview from './pages/ManualReview';
import AuditTrail from './pages/AuditTrail';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import { 
  fetchHealth, 
  fetchAnalytics, 
  fetchCases, 
  fetchManualReviews, 
  fetchAuditLogs, 
  fetchSettings, 
  seedDemoData, 
  analyzeCase, 
  recoverCase, 
  approveCase, 
  rejectCase, 
  updateSettings 
} from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [health, setHealth] = useState({ app_mode: 'mock', use_razorpay: false });
  const [analytics, setAnalytics] = useState(null);
  const [cases, setCases] = useState([]);
  const [manualCases, setManualCases] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [settingsData, setSettingsData] = useState(null);
  const [selectedCase, setSelectedCase] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [h, a, c, m, logs, s] = await Promise.all([
        fetchHealth().catch(() => ({ app_mode: 'mock', use_razorpay: false })),
        fetchAnalytics().catch(() => null),
        fetchCases().catch(() => []),
        fetchManualReviews().catch(() => []),
        fetchAuditLogs().catch(() => []),
        fetchSettings().catch(() => null)
      ]);
      setHealth(h);
      setAnalytics(a);
      setCases(c);
      setManualCases(m);
      setAuditLogs(logs);
      setSettingsData(s);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSeedData = async () => {
    setLoading(true);
    await seedDemoData();
    await loadData();
    setLoading(false);
  };

  const handleAnalyzeCase = async (id) => {
    await analyzeCase(id);
    await loadData();
    if (selectedCase && selectedCase.id === id) {
      const updated = await fetchCases({ id });
      if (updated && updated.length > 0) setSelectedCase(updated[0]);
    }
  };

  const handleExecuteRecovery = async (id) => {
    await recoverCase(id);
    await loadData();
    if (selectedCase && selectedCase.id === id) {
      const updated = await fetchCases({ id });
      if (updated && updated.length > 0) setSelectedCase(updated[0]);
    }
  };

  const handleApproveCase = async (id) => {
    await approveCase(id);
    await loadData();
    if (selectedCase && selectedCase.id === id) {
      const updated = await fetchCases({ id });
      if (updated && updated.length > 0) setSelectedCase(updated[0]);
    }
  };

  const handleRejectCase = async (id) => {
    await rejectCase(id, "Rejected by merchant operator");
    await loadData();
    if (selectedCase && selectedCase.id === id) {
      setSelectedCase(null);
    }
  };

  const handleSaveSettings = async (data) => {
    const updated = await updateSettings(data);
    setSettingsData(updated);
  };

  return (
    <div className="flex min-h-screen bg-[#0b0f19]">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        appMode={health.app_mode}
        useRazorpay={health.use_razorpay}
      />

      <main className="flex-1 overflow-x-hidden">
        {activeTab === 'overview' && (
          <Overview 
            analytics={analytics} 
            onSelectCase={(c) => setSelectedCase(c)}
            onSeedData={handleSeedData}
            onOpenCopilot={() => setActiveTab('copilot')}
            loading={loading}
          />
        )}

        {activeTab === 'copilot' && (
          <Copilot />
        )}

        {activeTab === 'cases' && (
          <Cases 
            cases={cases}
            onSelectCase={(c) => setSelectedCase(c)}
            onAnalyzeCase={handleAnalyzeCase}
            onExecuteRecovery={handleExecuteRecovery}
          />
        )}

        {activeTab === 'chargebacks' && (
          <Chargebacks />
        )}

        {activeTab === 'fraud' && (
          <FraudAlerts />
        )}

        {activeTab === 'agent' && (
          <RecoveryAgent 
            cases={cases}
            onAnalyzeCase={handleAnalyzeCase}
            onExecuteRecovery={handleExecuteRecovery}
          />
        )}

        {activeTab === 'review' && (
          <ManualReview 
            manualCases={manualCases}
            onApprove={handleApproveCase}
            onReject={handleRejectCase}
          />
        )}

        {activeTab === 'audit' && (
          <AuditTrail auditLogs={auditLogs} />
        )}

        {activeTab === 'analytics' && (
          <Analytics analytics={analytics} />
        )}

        {activeTab === 'settings' && (
          <Settings 
            settingsData={settingsData}
            onSaveSettings={handleSaveSettings}
          />
        )}
      </main>

      {/* Case Details Modal */}
      {selectedCase && (
        <CaseDetails 
          caseData={selectedCase}
          onClose={() => setSelectedCase(null)}
          onAnalyze={handleAnalyzeCase}
          onExecute={handleExecuteRecovery}
          onApprove={handleApproveCase}
          onReject={handleRejectCase}
        />
      )}
    </div>
  );
}
