import api from './api';

export const collegeService = {
  getProfile: () => api.get('/college/profile'),
  updateProfile: (data) => api.put('/college/profile', data),
  getQR: () => api.get('/college/qr'),
  regenerateQR: () => api.post('/college/qr/regenerate'),
  getRequests: (status) => api.get('/college/student-requests', { params: { status } }),
  getStudentRequests: (status) => api.get('/college/student-requests', { params: { status } }),
  respondRequest: (linkId, action) => api.post(`/college/student-requests/${linkId}/action`, { action }),
  acceptStudentRequest: (linkId) => api.post(`/college/student-requests/${linkId}/action`, { action: 'accept' }),
  rejectStudentRequest: (linkId) => api.post(`/college/student-requests/${linkId}/action`, { action: 'reject' }),
  getStudents: () => api.get('/college/students'),
  getLinkedStudents: () => api.get('/college/students'),
  removeStudent: (studentId) => api.post(`/college/students/${studentId}/remove`),
  getStudentDocuments: (studentId) => api.get(`/college/student/${studentId}/documents`),
  getDashboardStats: () => api.get('/college/dashboard-stats'),
  verifyDirect: (formData) => api.post('/verification/college', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
};

export default collegeService;
