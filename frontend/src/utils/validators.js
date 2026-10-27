export const isValidEmail = (email) => {
  if (!email) return false;
  const pattern = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
  return pattern.test(email);
};

export const isValidPhone = (phone) => {
  if (!phone) return true;
  const pattern = /^\+?[0-9]{7,15}$/;
  return pattern.test(phone.trim());
};

export const isValidFileSize = (file, maxSizeMB = 16) => {
  if (!file) return false;
  return file.size <= maxSizeMB * 1024 * 1024;
};

export const isValidFileType = (file, allowedExtensions = ['pdf', 'png', 'jpg', 'jpeg', 'webp']) => {
  if (!file || !file.name) return false;
  const ext = file.name.split('.').pop().toLowerCase();
  return allowedExtensions.includes(ext);
};
