import { useState } from 'react';
import { changePassword } from '../../services/authService';
import Input from '../common/Input';
import Button from '../common/Button';
import { showToast } from '../common/Toast';
import { validatePassword, getPasswordStrength } from '../../utils/validators';

const ChangePassword = () => {
  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  
  const passwordStrength = getPasswordStrength(formData.newPassword);
  
  const handleChange = (field) => (e) => {
    setFormData({ ...formData, [field]: e.target.value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };
  
  const validate = () => {
    const newErrors = {};
    
    if (!formData.currentPassword) {
      newErrors.currentPassword = 'Current password is required';
    }
    
    const passwordError = validatePassword(formData.newPassword);
    if (passwordError) {
      newErrors.newPassword = passwordError;
    }
    
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your new password';
    } else if (formData.newPassword !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    setIsLoading(true);
    
    try {
      await changePassword(formData.currentPassword, formData.newPassword);
      showToast('Password changed successfully', 'success');
      
      // Clear form
      setFormData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to change password';
      setErrors({ general: errorMessage });
      showToast(errorMessage, 'error');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Change Password</h2>
      
      {errors.general && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{errors.general}</p>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Current Password"
          type="password"
          value={formData.currentPassword}
          onChange={handleChange('currentPassword')}
          placeholder="Enter current password"
          error={errors.currentPassword}
          showPasswordToggle
          required
        />
        
        <div>
          <Input
            label="New Password"
            type="password"
            value={formData.newPassword}
            onChange={handleChange('newPassword')}
            placeholder="Enter new password"
            error={errors.newPassword}
            showPasswordToggle
            required
          />
          
          {formData.newPassword && (
            <div className="mt-2">
              <div className="flex gap-1 mb-1">
                {[1, 2, 3].map((level) => (
                  <div
                    key={level}
                    className={`h-1 flex-1 rounded ${
                      level <= passwordStrength.level
                        ? passwordStrength.color
                        : 'bg-gray-200'
                    }`}
                  />
                ))}
              </div>
              {passwordStrength.label && (
                <p className="text-xs text-gray-600">
                  Password strength: {passwordStrength.label}
                </p>
              )}
            </div>
          )}
        </div>
        
        <Input
          label="Confirm New Password"
          type="password"
          value={formData.confirmPassword}
          onChange={handleChange('confirmPassword')}
          placeholder="Confirm new password"
          error={errors.confirmPassword}
          showPasswordToggle
          required
        />
        
        <Button
          type="submit"
          loading={isLoading}
          disabled={isLoading}
        >
          Change Password
        </Button>
      </form>
    </div>
  );
};

export default ChangePassword;
