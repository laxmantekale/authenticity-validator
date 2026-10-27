import api from './api';

export const blockchainService = {
  getDocumentRecord: (docHash) => api.get(`/blockchain/${docHash}`)
};

export default blockchainService;
