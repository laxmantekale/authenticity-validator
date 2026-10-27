import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import { Menu, ExternalLink } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const DashboardLayout = ({ role = 'student' }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(() => {
    try {
      return localStorage.getItem('sidebar_collapsed') === 'true';
    } catch {
      return false;
    }
  });

  const toggleCollapse = () => {
    setCollapsed((prev) => {
      const next = !prev;
      try {
        localStorage.setItem('sidebar_collapsed', String(next));
      } catch {}
      return next;
    });
  };

  const location = useLocation();
  const { user } = useAuth();

  // Format breadcrumb text
  const currentPathSegment = location.pathname.split('/').filter(Boolean).pop();
  const pageTitle = currentPathSegment
    ? currentPathSegment.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
    : 'Dashboard';

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col md:flex-row">
      {/* Desktop Collapsible Sidebar */}
      <div
        className={`hidden md:block ${
          collapsed ? 'w-20' : 'w-64'
        } shrink-0 h-screen sticky top-0 transition-all duration-300 ease-in-out z-30`}
      >
        <Sidebar
          role={role}
          collapsed={collapsed}
          onToggleCollapse={toggleCollapse}
        />
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          <div
            className="fixed inset-0 bg-slate-950/60 backdrop-blur-xs transition-opacity"
            onClick={() => setMobileOpen(false)}
          />
          <div className="relative w-64 max-w-[80%] bg-slate-900 z-10 h-full shadow-2xl flex flex-col">
            <Sidebar
              role={role}
              onCloseMobile={() => setMobileOpen(false)}
              collapsed={false}
            />
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        {/* Top Header Bar */}
        <header className="h-16 bg-white border-b border-slate-200/80 px-4 sm:px-6 lg:px-8 flex items-center justify-between sticky top-0 z-20 shadow-xs">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileOpen(true)}
              className="md:hidden p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors cursor-pointer"
              aria-label="Open sidebar"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                {role === 'college' ? 'Institution' : 'Student'}
              </span>
              <span className="text-slate-300">•</span>
              <span className="text-xs font-semibold text-slate-700">
                {pageTitle}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/"
              target="_blank"
              rel="noreferrer"
              className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-colors"
            >
              <span>Public Portal</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </Link>

            <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
              <div className="w-8 h-8 rounded-full bg-blue-50 border border-blue-200 text-blue-700 flex items-center justify-center font-bold text-xs">
                {user?.name ? user.name.charAt(0).toUpperCase() : role === 'college' ? 'C' : 'S'}
              </div>
              <div className="hidden lg:block text-left">
                <p className="text-xs font-semibold text-slate-900 leading-tight truncate max-w-[150px]">
                  {user?.name || user?.email}
                </p>
                <p className="text-[10px] text-slate-500 uppercase tracking-wider">{role}</p>
              </div>
            </div>
          </div>
        </header>

        {/* Dynamic Page Content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
