import React, { useState, useEffect } from 'react';
import { User, Mail, Phone, Calendar, Save, Loader2, CheckCircle2, Lock, Eye, EyeOff, Building2, ShieldCheck, KeyRound } from 'lucide-react';
import { studentService } from '../../services/studentService';
import { authService } from '../../services/authService';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import SectionCard from '../../components/common/SectionCard';
import LoadingState from '../../components/common/LoadingState';

export const MyProfile = () => {
  const { toast } = useToast();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ full_name: '', mobile: '' });

  // Password change state
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const res = await studentService.getProfile();
      const p = res.data.profile;
      setProfile(p);
      setForm({
        full_name: p.full_name || '',
        mobile: p.mobile || ''
      });
    } catch (err) {
      toast.error('Unable to retrieve profile details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      await studentService.updateProfile(form);
      toast.success('Profile details updated successfully');
      fetchProfile();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (passwordForm.new_password.length < 6) {
      toast.error('New password must be at least 6 characters long');
      return;
    }
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('New passwords do not match');
      return;
    }

    try {
      setChangingPassword(true);
      await authService.changePassword(
        passwordForm.current_password,
        passwordForm.new_password,
        passwordForm.confirm_password
      );
      toast.success('Password changed successfully');
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to update password. Check your current password.');
    } finally {
      setChangingPassword(false);
    }
  };

  if (loading) {
    return <LoadingState message="Loading student profile details..." />;
  }

  return (
    <div className="max-w-4xl space-y-6">
      <PageHeader
        title="My Profile"
        subtitle="Manage your student account information, personal credentials, and security settings"
        badge={`ID: ${profile?.student_id || 'STU'}`}
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left ID Card */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs text-center space-y-4 h-fit">
          <div className="w-20 h-20 rounded-full bg-blue-50 border-2 border-blue-200 text-blue-600 flex items-center justify-center font-bold text-2xl mx-auto shadow-xs">
            {profile?.full_name ? profile.full_name.charAt(0).toUpperCase() : 'S'}
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">{profile?.full_name}</h3>
            <p className="text-xs text-slate-500 font-mono mt-0.5">{profile?.student_id}</p>
          </div>

          <div className="pt-3 border-t border-slate-100 text-left space-y-2.5 text-xs text-slate-600">
            <div className="flex items-center gap-2">
              <Mail className="w-4 h-4 text-slate-400 shrink-0" />
              <div className="truncate">
                <span className="text-[10px] text-slate-400 block">Registered Email</span>
                <span className="font-medium text-slate-800">{profile?.email || 'Not available'}</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Phone className="w-4 h-4 text-slate-400 shrink-0" />
              <div>
                <span className="text-[10px] text-slate-400 block">Phone</span>
                <span className="font-medium text-slate-800">{profile?.mobile || 'Not provided'}</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Building2 className="w-4 h-4 text-slate-400 shrink-0" />
              <div>
                <span className="text-[10px] text-slate-400 block">Connected Institution</span>
                <span className="font-medium text-slate-800">{profile?.college_name || 'Not Connected'}</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-slate-400 shrink-0" />
              <div>
                <span className="text-[10px] text-slate-400 block">Account Created</span>
                <span className="font-medium text-slate-800">
                  {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'Active'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Forms: Edit Profile & Change Password */}
        <div className="md:col-span-2 space-y-6">
          {/* Edit Profile */}
          <SectionCard title="Personal Information" subtitle="Update your profile information">
            <form onSubmit={handleUpdate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Full Legal Name</label>
                <div className="relative">
                  <User className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                  <input
                    type="text"
                    required
                    value={form.full_name}
                    onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                    className="w-full pl-9 pr-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-800 shadow-xs"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Registered Email Address (Read-only)</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                  <input
                    type="email"
                    disabled
                    value={profile?.email || ''}
                    className="w-full pl-9 pr-3 py-2 bg-slate-100 border border-slate-200 rounded-lg text-xs text-slate-600 font-medium cursor-not-allowed"
                  />
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Your registered email address is verified and permanently linked to your student ID.</p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Mobile Contact Number</label>
                <div className="relative">
                  <Phone className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                  <input
                    type="tel"
                    required
                    value={form.mobile}
                    onChange={(e) => setForm({ ...form, mobile: e.target.value })}
                    className="w-full pl-9 pr-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-800 shadow-xs"
                  />
                </div>
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  type="submit"
                  disabled={saving}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:bg-slate-600"
                >
                  {saving ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Saving Changes...</span>
                    </>
                  ) : (
                    <>
                      <Save className="w-3.5 h-3.5" />
                      <span>Save Profile Changes</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </SectionCard>

          {/* Change Password */}
          <SectionCard title="Security & Password" subtitle="Update your account password regularly to keep your credentials safe">
            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Current Password</label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                  <input
                    type={showCurrentPassword ? 'text' : 'password'}
                    required
                    value={passwordForm.current_password}
                    onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                    placeholder="Enter your current password"
                    className="w-full pl-9 pr-10 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-800 shadow-xs"
                  />
                  <button
                    type="button"
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                    className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 cursor-pointer"
                  >
                    {showCurrentPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">New Password</label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                    <input
                      type={showNewPassword ? 'text' : 'password'}
                      required
                      value={passwordForm.new_password}
                      onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                      placeholder="Min. 6 characters"
                      className="w-full pl-9 pr-10 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-800 shadow-xs"
                    />
                    <button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 cursor-pointer"
                    >
                      {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Confirm New Password</label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                    <input
                      type="password"
                      required
                      value={passwordForm.confirm_password}
                      onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                      placeholder="Re-type new password"
                      className="w-full pl-9 pr-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-800 shadow-xs"
                    />
                  </div>
                </div>
              </div>

              {passwordForm.confirm_password && passwordForm.new_password !== passwordForm.confirm_password && (
                <p className="text-[11px] text-rose-600 font-medium">New passwords do not match</p>
              )}

              <div className="pt-2 flex justify-end">
                <button
                  type="submit"
                  disabled={changingPassword || (passwordForm.confirm_password && passwordForm.new_password !== passwordForm.confirm_password)}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:bg-slate-600"
                >
                  {changingPassword ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Updating Password...</span>
                    </>
                  ) : (
                    <>
                      <KeyRound className="w-3.5 h-3.5" />
                      <span>Update Password</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </SectionCard>
        </div>

      </div>
    </div>
  );
};

export default MyProfile;
