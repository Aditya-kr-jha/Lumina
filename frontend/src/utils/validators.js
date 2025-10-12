import { VALIDATION_RULES, FILE_SIZE_LIMITS } from './constants';

/**
 * Validate username
 * @param {string} username
 * @returns {string|null} Error message or null if valid
 */
export const validateUsername = (username) => {
  if (!username) return 'Username is required';
  if (username.length < VALIDATION_RULES.USERNAME.MIN_LENGTH) {
    return `Username must be at least ${VALIDATION_RULES.USERNAME.MIN_LENGTH} characters`;
  }
  if (username.length > VALIDATION_RULES.USERNAME.MAX_LENGTH) {
    return `Username must be less than ${VALIDATION_RULES.USERNAME.MAX_LENGTH} characters`;
  }
  if (!VALIDATION_RULES.USERNAME.PATTERN.test(username)) {
    return 'Username can only contain letters, numbers, and underscores';
  }
  return null;
};

/**
 * Validate email
 * @param {string} email
 * @returns {string|null} Error message or null if valid
 */
export const validateEmail = (email) => {
  if (!email) return 'Email is required';
  if (!VALIDATION_RULES.EMAIL.PATTERN.test(email)) {
    return 'Please enter a valid email address';
  }
  return null;
};

/**
 * Validate password
 * @param {string} password
 * @returns {string|null} Error message or null if valid
 */
export const validatePassword = (password) => {
  if (!password) return 'Password is required';
  if (password.length < VALIDATION_RULES.PASSWORD.MIN_LENGTH) {
    return `Password must be at least ${VALIDATION_RULES.PASSWORD.MIN_LENGTH} characters`;
  }
  return null;
};

/**
 * Check password strength
 * @param {string} password
 * @returns {object} Strength info { level, label, color }
 */
export const getPasswordStrength = (password) => {
  if (!password) return { level: 0, label: '', color: '' };
  
  let strength = 0;
  if (password.length >= 8) strength++;
  if (password.length >= 12) strength++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
  if (/\d/.test(password)) strength++;
  if (/[^a-zA-Z\d]/.test(password)) strength++;
  
  if (strength <= 2) return { level: 1, label: 'Weak', color: 'bg-red-500' };
  if (strength <= 3) return { level: 2, label: 'Medium', color: 'bg-yellow-500' };
  return { level: 3, label: 'Strong', color: 'bg-green-500' };
};

/**
 * Validate question
 * @param {string} question
 * @returns {string|null} Error message or null if valid
 */
export const validateQuestion = (question) => {
  if (!question || !question.trim()) return 'Question cannot be empty';
  if (question.length > VALIDATION_RULES.QUESTION.MAX_LENGTH) {
    return `Question must be less than ${VALIDATION_RULES.QUESTION.MAX_LENGTH} characters`;
  }
  return null;
};

/**
  * Validate file
 * @param {File} file
 * @returns {string|null} Error message or null if valid
 */
export const validateFile = (file) => {
  if (!file) return 'No file selected';

  const { MAX_FILE_SIZE, ACCEPTED_MIME_TYPES, ACCEPTED_FORMATS } = FILE_SIZE_LIMITS;

  if (file.size > MAX_FILE_SIZE) {
    const mb = Math.round((MAX_FILE_SIZE / (1024 * 1024)) * 10) / 10;
    return `File size must be less than ${mb}MB`;
  }

  // Some browsers may not set file.type on drag/drop; fall back to extension check
  const typeOk = file.type && ACCEPTED_MIME_TYPES.includes(file.type);
  const ext = '.' + (file.name.split('.').pop() || '').toLowerCase();
  const extOk = ACCEPTED_FORMATS.includes(ext);

  if (!(typeOk || extOk)) {
    return 'Only PDF files are supported';
  }

  return null;
};
