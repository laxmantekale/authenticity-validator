import React, { useState } from 'react';
import { Settings as SettingsIcon, Lock, Bell, Shield, Save, CheckCircle2 } from 'lucide-react';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import SectionCard from '../../components/common/SectionCard';

export const Settings = () => {
  const { toast } = useToast();
  const [notifyVerification, setNotifyVerification] = useState(true);
  const [notifyRequests, setNotifyRequests] = useState(true);
  const [passForm, setPassForm] = useState({ current: '', new_pass: '', confirm: '' });

  const handleSaveSecurity = (e) => {
    e.preventDefault();
    if (passForm.new_pass && passForm.new_pass !== passForm.confirm) {
      toast.error('New passwords do not match.');
      return;
    }
    toast.success('Security preferences updated successfully.');
    setPassForm({ current: '', new_pass: '', confirm: '' });
  };

  return (
    <div className="max-w-4xl space-y-6">
      <PageHeader
        title="Account Settings"
        subtitle="Manage your security preferences, alerts, and verification options"
      />

      <div className="space-y-6">
        
        {/* Notifications */}
        <SectionCard title="Notification Preferences" subtitle="Control when you receive system alerts and updates">
          <div className="space-y-4 text-xs">
            <label className="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-slate-50/50 cursor-pointer">
              <div>
                <p className="font-semibold text-slate-900">Verification Result Alerts</p>
                <p className="text-slate-500 text-[11px]">Notify me immediately when an automated verification pipeline completes</p>
              </div>
              <input
                type="checkbox"
                checked={notifyVerification}
                onChange={(e) => setNotifyVerification(e.target.checked)}
                className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-slate-50/50 cursor-pointer">
              <div>
                <p className="font-semibold text-slate-900">College Link Request Updates</p>
                <p className="text-slate-500 text-[11px]">Notify me when a college accepts or responds to my connection request</p>
              </div>
              <input
                type="checkbox"
                checked={notifyRequests}
                onChange={(e) => setNotifyRequests(e.target.checked)}
                className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300"
              />
            </label>
          </div>
        </SectionCard>

        {/* Password & Security */}
        <SectionCard title="Security & Authentication" subtitle="Update your student portal login password">
          <form onSubmit={handleSaveSecurity} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Current Password</label>
                <input
                  type="password"
                  value={passForm.current}
                  onChange={(e) => setPassForm({ ...passForm, current: e.target.value })}
                  placeholder="••••••••"
                  className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-800 shadow-xs"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">New Password</label>
                <input
                  type="password"
                  value={passForm.new_pass}
                  onChange={(e) => setPassForm({ ...passForm, new_pass: e.target.value })}
                  placeholder="••••••••"
                  className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-800 shadow-xs"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Confirm New Password</label>
                <input
                  type="password"
                  value={passForm.confirm}
                  onChange={(e) => setPassForm({ ...passForm, confirm: e.target.value })}
                  placeholder="••••••••"
                  className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-800 shadow-xs"
                />
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                type="submit"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer"
              >
                <Save className="w-3.5 h-3.5" />
                <span>Save Security Preferences</span>
              </button>
            </div>
          </form>
        </SectionCard>

      </div>
    </div>
  );
};

export default Settings;
