import api from './api';
import { API_ENDPOINTS, STORAGE_KEYS } from '../config/api';

/**
 * Login user
 * @param {string} username
 * @param {string} password
 * @returns {Promise<object>} Token data
 */
export const login = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  // Use fetch with the absolute TOKEN URL
  const response = await fetch(API_ENDPOINTS.TOKEN, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  const data = await response.json();
  
  // Store token
  localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, data.access_token);
  
  return data;
};

/**
 * Register new user
 * @param {object} userData - { username, email, password }
 * @returns {Promise<object>} User data
 */
export const register = async (userData) => {
  const response = await api.post(API_ENDPOINTS.REGISTER, {
    ...userData,
    status: 'ACTIVE',
  });
  return response.data;
};

/**
 * Get current user profile
 * @returns {Promise<object>} User data
 */
export const getUserProfile = async () => {
  const response = await api.get(API_ENDPOINTS.USER_ME);
  return response.data;
};

/**
 * Update user email
 * @param {string} email
 * @returns {Promise<object>} Updated user data
 */
export const updateUserEmail = async (email) => {
  const response = await api.patch(API_ENDPOINTS.USER_ME, { email });
  return response.data;
};

/**
 * Change user password
 * @param {string} currentPassword
 * @param {string} newPassword
 * @returns {Promise<object>} Success message
 */
export const changePassword = async (currentPassword, newPassword) => {
  const response = await api.post(API_ENDPOINTS.USER_CHANGE_PASSWORD, {
    current_password: currentPassword,
    new_password: newPassword,
  });
  return response.data;
};

/**
 * Delete user account
 * @returns {Promise<object>} Success message
 */
export const deleteAccount = async () => {
  const response = await api.delete(API_ENDPOINTS.USER_DELETE);
  return response.data;
};

/**
 * Logout user
 */
export const logout = () => {
  localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
};
