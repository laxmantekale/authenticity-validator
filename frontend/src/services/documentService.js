import api from './api';

export const documentService = {
  getMyDocuments: (params = {}) => api.get('/documents/my-documents', { params }),
  getDirectDocuments: () => api.get('/documents/my-documents', { params: { source: 'direct' } }),
  getLinkedDocuments: () => api.get('/documents/my-documents', { params: { source: 'linked' } }),
  getDocumentDetails: (id) => api.get(`/documents/${id}`),
  uploadDocument: (formData) => api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  deleteDocument: (id) => api.delete(`/documents/${id}`),
  viewDocumentUrl: (id) => `/api/documents/${id}/view`
};

export default documentService;
