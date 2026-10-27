import api from './api';

export const studentService = {
  getProfile: () => api.get('/student/profile'),
  updateProfile: (data) => api.put('/student/profile', data),
  getColleges: () => api.get('/student/colleges'),
  getLinkedColleges: () => api.get('/student/colleges'),
  searchColleges: (query) => api.get('/student/colleges/search', { params: { query } }),
  requestCollegeLink: (collegeId) => api.post('/student/colleges/request-link', { college_id: collegeId }),
  requestLink: (collegeId) => api.post('/student/colleges/request-link', { college_id: collegeId }),
  unlinkCollege: (collegeId) => api.post(`/student/colleges/${collegeId}/unlink`),
  getDashboardStats: () => api.get('/student/dashboard-stats')
};

export default studentService;
