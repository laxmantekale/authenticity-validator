import api from './api';

export const reportService = {
  getMyReports: () => api.get('/reports/my-reports'),
  getReportDetails: (reportId) => api.get(`/reports/${reportId}/details`),
  downloadSingleReport: (reportId) => api.get(`/reports/download/${reportId}`, { responseType: 'blob' }),
  downloadReportJson: (reportId) => api.get(`/reports/${reportId}/json`, { responseType: 'blob' }),
  downloadCompleteStudentReport: () => api.get('/reports/download-complete', { responseType: 'blob' }),
  downloadCollegeStudentReport: (studentId) => api.get(`/reports/student/${studentId}/download-complete`, { responseType: 'blob' }),
  downloadCollegeAudit: () => api.get('/reports/college/download-audit', { responseType: 'blob' })
};

export default reportService;
