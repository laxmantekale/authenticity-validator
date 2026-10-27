import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  User,
  Building2,
  ShieldCheck,
  FileText,
  History,
  Award,
  Settings,
  LogOut,
  QrCode,
  Users,
  UserCheck,
  FolderOpen,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';

export const Sidebar = ({
  role = 'student',
  onCloseMobile,
  collapsed = false,
  onToggleCollapse
}) => {
  const { user, logout } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    toast.info('Logged out successfully');
    navigate('/');
  };

  const studentNavItems = [
    { name: 'Dashboard', path: '/student/dashboard', icon: LayoutDashboard },
    { name: 'Verify Document', path: '/student/verify', icon: ShieldCheck },
    { name: 'Verification History', path: '/student/history', icon: History },
    { name: 'Reports', path: '/student/reports', icon: Award },
    { name: 'My Documents', path: '/student/documents', icon: FileText },
    { name: 'College Connections', path: '/student/colleges', icon: Building2 },
    { name: 'Profile', path: '/student/profile', icon: User },
    { name: 'Settings', path: '/student/settings', icon: Settings }
  ];

  const collegeNavItems = [
    { name: 'Dashboard', path: '/college/dashboard', icon: LayoutDashboard },
    { name: 'Documents', path: '/college/documents', icon: FolderOpen },
    { name: 'Students', path: '/college/students', icon: Users },
    { name: 'Connection Requests', path: '/college/student-requests', icon: UserCheck },
    { name: 'Verification History', path: '/college/history', icon: History },
    { name: 'Verify Document', path: '/college/verification', icon: ShieldCheck },
    { name: 'Reports', path: '/college/reports', icon: Award },
    { name: 'Profile', path: '/college/profile', icon: Building2 },
    { name: 'College QR', path: '/college/qr', icon: QrCode },
    { name: 'Settings', path: '/college/settings', icon: Settings }
  ];

  const navItems = role === 'college' ? collegeNavItems : studentNavItems;

  return (
    <aside
      className={`${
        collapsed ? 'w-20' : 'w-64'
      } bg-slate-900 text-slate-300 flex flex-col h-full border-r border-slate-800 shadow-sm select-none transition-all duration-300 ease-in-out`}
    >
      {/* Brand Header */}
      <div
        className={`p-4 border-b border-slate-800 flex items-center ${
          collapsed ? 'justify-center' : 'justify-between'
        } gap-2`}
      >
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-9 h-9 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0">
            <ShieldCheck className="w-5 h-5 text-blue-400" />
          </div>
          {!collapsed && (
            <div className="min-w-0 flex-1">
              <h2 className="text-xs font-bold text-white tracking-tight truncate">
                Authentication Validator
              </h2>
              <p className="text-[11px] text-slate-400 truncate">
                {role === 'college' ? 'Institution Workspace' : 'Student Workspace'}
              </p>
            </div>
          )}
        </div>
        {onToggleCollapse && (
          <button
            type="button"
            onClick={onToggleCollapse}
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            className="hidden md:flex p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer shrink-0"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        )}
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onCloseMobile}
              className={({ isActive }) =>
                `group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                  collapsed ? 'justify-center px-0' : ''
                } ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-xs font-semibold'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/80'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              {!collapsed && <span className="truncate">{item.name}</span>}
              {collapsed && (
                <span className="absolute left-full ml-3 px-2.5 py-1.5 bg-slate-900 border border-slate-700 text-white text-xs font-semibold rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all pointer-events-none whitespace-nowrap z-50">
                  {item.name}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* User Profile & Logout Footer */}
      <div className="p-3 border-t border-slate-800 space-y-2">
        <div
          className={`px-2.5 py-2 rounded-xl bg-slate-800/60 border border-slate-700/50 flex items-center ${
            collapsed ? 'justify-center' : 'gap-2.5'
          } group relative`}
        >
          <div className="w-7 h-7 rounded-lg bg-blue-500/20 text-blue-300 flex items-center justify-center font-bold text-xs shrink-0">
            {user?.name ? user.name.charAt(0).toUpperCase() : role === 'college' ? 'C' : 'S'}
          </div>
          {!collapsed && (
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold text-white truncate">
                {user?.name || user?.email || 'Active User'}
              </p>
              <p className="text-[10px] text-slate-400 capitalize truncate">{role} Account</p>
            </div>
          )}
          {collapsed && (
            <span className="absolute left-full ml-3 px-2.5 py-1.5 bg-slate-900 border border-slate-700 text-white text-xs font-semibold rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all pointer-events-none whitespace-nowrap z-50">
              {user?.name || user?.email || 'Active User'} ({role})
            </span>
          )}
        </div>

        <button
          onClick={handleLogout}
          title={collapsed ? 'Logout' : undefined}
          className={`w-full flex items-center ${
            collapsed ? 'justify-center px-0' : 'gap-2.5 px-3'
          } py-2 rounded-xl text-xs font-medium text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors cursor-pointer group relative`}
        >
          <LogOut className="w-4 h-4 shrink-0" />
          {!collapsed && <span>Logout</span>}
          {collapsed && (
            <span className="absolute left-full ml-3 px-2.5 py-1.5 bg-slate-900 border border-slate-700 text-rose-300 text-xs font-semibold rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all pointer-events-none whitespace-nowrap z-50">
              Logout
            </span>
          )}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
