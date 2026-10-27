import React, { useState } from 'react';
import { Settings as SettingsIcon, Bell, Shield, Save, CheckCircle2, Building2 } from 'lucide-react';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import SectionCard from '../../components/common/SectionCard';

export const CollegeSettings = () => {
  const { toast } = useToast();
  const [notifyOnNewLink, setNotifyOnNewLink] = useState(true);
  const [autoVerifyKnown, setAutoVerifyKnown] = useState(true);
  const [retentionPeriod, setRetentionPeriod] = useState('7_YEARS');

  const handleSave = (e) => {
    e.preventDefault();
    toast.success('Institution security and notification preferences updated.');
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <PageHeader
        title="Institution Settings & Security Policies"
        subtitle="Configure incoming linking alerts, document retention policies, and automated verification rules"
      />

      <form onSubmit={handleSave} className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2 mb-3">
            <Bell className="w-4 h-4 text-blue-600" />
            Admissions & Link Notifications
          </h3>
          <div className="space-y-3 text-xs sm:text-sm">
            <label className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-100/60 transition-colors">
              <div>
                <p className="font-semibold text-slate-800">Direct Notification on Candidate Link Request</p>
                <p className="text-xs text-slate-500">Receive an email alert when a student scans institutional QR or connects online</p>
              </div>
              <input
                type="checkbox"
                checked={notifyOnNewLink}
                onChange={(e) => setNotifyOnNewLink(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </label>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2 mb-3">
            <Shield className="w-4 h-4 text-blue-600" />
            Verification Engine Policies
          </h3>
          <div className="space-y-3 text-xs sm:text-sm">
            <label className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-100/60 transition-colors">
              <div>
                <p className="font-semibold text-slate-800">High-Precision OCR & Font Discrepancy Scrutiny</p>
                <p className="text-xs text-slate-500">Enforce dual-pass pixel alignment and font analysis on all direct uploads</p>
              </div>
              <input
                type="checkbox"
                checked={autoVerifyKnown}
                onChange={(e) => setAutoVerifyKnown(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </label>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100">
          <label className="block text-xs font-semibold text-slate-700 mb-1">Audit Trail Retention Standard</label>
          <select
            value={retentionPeriod}
            onChange={(e) => setRetentionPeriod(e.target.value)}
            className="w-full px-3.5 py-2.5 bg-white border border-slate-200 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <option value="5_YEARS">5 Years (Standard UGC Academic Compliance)</option>
            <option value="7_YEARS">7 Years (Recommended Regulatory Audit Window)</option>
            <option value="PERMANENT">Permanent Archival (Immutable Cryptographic Ledger)</option>
          </select>
        </div>

        <div className="pt-4 border-t border-slate-100 flex justify-end">
          <button
            type="submit"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg text-xs sm:text-sm transition-colors shadow-xs"
          >
            <Save className="w-4 h-4" />
            <span>Save Preferences</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default CollegeSettings;
