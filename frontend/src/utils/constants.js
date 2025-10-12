// Application constants

export const FILE_SIZE_LIMITS = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ACCEPTED_FORMATS: ['.pdf'],
  ACCEPTED_MIME_TYPES: ['application/pdf'],
};

export const VALIDATION_RULES = {
  USERNAME: {
    MIN_LENGTH: 3,
    MAX_LENGTH: 50,
    PATTERN: /^[a-zA-Z0-9_]+$/,
  },
  PASSWORD: {
    MIN_LENGTH: 8,
  },
  EMAIL: {
    PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
  QUESTION: {
    MIN_LENGTH: 1,
    MAX_LENGTH: 1000,
  },
};

export const DOCUMENT_STATUS = {
  READY: 'ready',
  PROCESSING: 'processing',
  ERROR: 'error',
};

export const USER_ROLES = {
  USER: 'user',
  ADMIN: 'admin',
};

export const USER_STATUS = {
  ACTIVE: 'ACTIVE',
  INACTIVE: 'INACTIVE',
};

export const CHAT_CONFIG = {
  DEFAULT_TOP_K: 4,
  POLLING_INTERVAL: 2000,
  MESSAGE_MAX_ROWS: 5,
};

export const TOAST_DURATION = 3000;

export const EXAMPLE_QUESTIONS = [
  "What is this document about?",
  "Summarize the key points",
  "What are the main findings?",
  "Explain the methodology used",
];
