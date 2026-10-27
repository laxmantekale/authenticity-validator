import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';

// Layouts
import PublicLayout from './components/common/PublicLayout';
import DashboardLayout from './components/common/DashboardLayout';

// Public Pages
import HomePage from './pages/public/HomePage';
import AboutPage from './pages/public/AboutPage';
import HowItWorksPage from './pages/public/HowItWorksPage';
import FeaturesPage from './pages/public/FeaturesPage';
import ContactPage from './pages/public/ContactPage';
import CollegeConnectPage from './pages/public/CollegeConnectPage';

// Auth Pages
import LoginPage from './pages/auth/LoginPage';
import StudentLoginPage from './pages/auth/StudentLoginPage';
import StudentRegisterPage from './pages/auth/StudentRegisterPage';
import CollegeLoginPage from './pages/auth/CollegeLoginPage';
import CollegeRegisterPage from './pages/auth/CollegeRegisterPage';
import ForgotPassword from './pages/auth/ForgotPassword';
import ResetPassword from './pages/auth/ResetPassword';

// Student Pages
import StudentDashboard from './pages/student/StudentDashboard';
import MyProfile from './pages/student/MyProfile';
import MyColleges from './pages/student/MyColleges';
import VerifyDocument from './pages/student/VerifyDocument';
import MyDocuments from './pages/student/MyDocuments';
import VerificationHistory from './pages/student/VerificationHistory';
import MyReports from './pages/student/MyReports';
import Settings from './pages/student/Settings';

// College Pages
import CollegeDashboard from './pages/college/CollegeDashboard';
import CollegeProfile from './pages/college/CollegeProfile';
import CollegeQR from './pages/college/CollegeQR';
import StudentRequests from './pages/college/StudentRequests';
import Students from './pages/college/Students';
import Documents from './pages/college/Documents';
import CollegeVerification from './pages/college/CollegeVerification';
import CollegeReports from './pages/college/CollegeReports';
import CollegeHistory from './pages/college/CollegeHistory';
import CollegeSettings from './pages/college/CollegeSettings';

// Protected Route wrappers
const StudentRoute = ({ children }) => {
  const { user, loading, isStudent } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full" />
      </div>
    );
  }
  if (!user || !isStudent) {
    return <Navigate to="/student/login" replace />;
  }
  return children;
};

const CollegeRoute = ({ children }) => {
  const { user, loading, isCollege } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full" />
      </div>
    );
  }
  if (!user || !isCollege) {
    return <Navigate to="/college/login" replace />;
  }
  return children;
};

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Pages */}
            <Route element={<PublicLayout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/how-it-works" element={<HowItWorksPage />} />
              <Route path="/features" element={<FeaturesPage />} />
              <Route path="/contact" element={<ContactPage />} />
              <Route path="/college-connect/:identifier" element={<CollegeConnectPage />} />
              
              {/* Auth Routes inside public layout */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password/:token" element={<ResetPassword />} />
              <Route path="/student/login" element={<StudentLoginPage />} />
              <Route path="/student/register" element={<StudentRegisterPage />} />
              <Route path="/college/login" element={<CollegeLoginPage />} />
              <Route path="/college/register" element={<CollegeRegisterPage />} />
            </Route>

            {/* Student Protected Portal */}
            <Route
              path="/student"
              element={
                <StudentRoute>
                  <DashboardLayout role="student" />
                </StudentRoute>
              }
            >
              <Route path="dashboard" element={<StudentDashboard />} />
              <Route path="profile" element={<MyProfile />} />
              <Route path="colleges" element={<MyColleges />} />
              <Route path="verify" element={<VerifyDocument />} />
              <Route path="documents" element={<MyDocuments />} />
              <Route path="history" element={<VerificationHistory />} />
              <Route path="reports" element={<MyReports />} />
              <Route path="settings" element={<Settings />} />
            </Route>

            {/* College Protected Portal */}
            <Route
              path="/college"
              element={
                <CollegeRoute>
                  <DashboardLayout role="college" />
                </CollegeRoute>
              }
            >
              <Route path="dashboard" element={<CollegeDashboard />} />
              <Route path="profile" element={<CollegeProfile />} />
              <Route path="qr" element={<CollegeQR />} />
              <Route path="student-requests" element={<StudentRequests />} />
              <Route path="requests" element={<StudentRequests />} />
              <Route path="students" element={<Students />} />
              <Route path="documents" element={<Documents />} />
              <Route path="verification" element={<CollegeVerification />} />
              <Route path="verify" element={<CollegeVerification />} />
              <Route path="reports" element={<CollegeReports />} />
              <Route path="history" element={<CollegeHistory />} />
              <Route path="settings" element={<CollegeSettings />} />
            </Route>

            {/* Catch-all fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ToastProvider>
  );
}

export default App;
