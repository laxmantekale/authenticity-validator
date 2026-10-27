import api from './api';

export const authService = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  loginStudent: (email, password) => api.post('/auth/student/login', { email, password }),
  registerStudent: (data) => api.post('/auth/student/register', data),
  loginCollege: (email, password) => api.post('/auth/college/login', { email, password }),
  registerCollege: (data) => api.post('/auth/college/register', data),
  getCurrentUser: () => api.get('/auth/me'),
  forgotPassword: (email) => api.post('/auth/forgot-password', { email }),
  resetPassword: (token, password, confirm_password) => api.post('/auth/reset-password', { token, password, confirm_password: confirm_password || password }),
  changePassword: (current_password, new_password, confirm_password) => api.post('/auth/change-password', { current_password, new_password, confirm_password: confirm_password || new_password })
};

export default authService;
