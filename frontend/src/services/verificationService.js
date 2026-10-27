import api from './api';

export const verificationService = {
  verifyDocument: (docId) => api.post(`/verification/verify/${docId}`),
  verifyStudentDirect: (formData) => api.post('/verification/student', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  verifyCollegeDirect: (formData) => api.post('/verification/college', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getStudentHistory: () => api.get('/history/student'),
  getCollegeHistory: () => api.get('/history/college'),
  getStatus: (verificationId) => api.get(`/verification/status/${verificationId}`)
};

export default verificationService;
