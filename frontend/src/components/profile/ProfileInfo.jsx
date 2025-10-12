import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { updateUserEmail } from '../../services/authService';
import Input from '../common/Input';
import Button from '../common/Button';
import { showToast } from '../common/Toast';
import { validateEmail } from '../../utils/validators';
import { formatDate } from '../../utils/formatters';

const ProfileInfo = () => {
  const { user, updateUser } = useAuth();
  const [email, setEmail] = useState(user?.email || '');
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleSave = async () => {
    const emailError = validateEmail(email);
    if (emailError) {
      setError(emailError);
      return;
    }
    
    if (email === user?.email) {
      setIsEditing(false);
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      const updatedUser = await updateUserEmail(email);
      updateUser(updatedUser);
      showToast('Email updated successfully', 'success');
      setIsEditing(false);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to update email';
      setError(errorMessage);
      showToast(errorMessage, 'error');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleCancel = () => {
    setEmail(user?.email || '');
    setError('');
    setIsEditing(false);
  };
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Profile Information</h2>
      
      <div className="space-y-4">
        {/* Username */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Username
          </label>
          <p className="text-gray-900">{user?.username}</p>
          <p className="text-xs text-gray-500 mt-1">Username cannot be changed</p>
        </div>
        
        {/* Email */}
        <div>
          {isEditing ? (
            <>
              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={error}
              />
              <div className="flex gap-2 mt-2">
                <Button
                  onClick={handleSave}
                  size="sm"
                  loading={isLoading}
                  disabled={isLoading}
                >
                  Save
                </Button>
                <Button
                  onClick={handleCancel}
                  size="sm"
                  variant="secondary"
                  disabled={isLoading}
                >
                  Cancel
                </Button>
              </div>
            </>
          ) : (
            <>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <div className="flex items-center justify-between">
                <p className="text-gray-900">{user?.email}</p>
                <Button
                  onClick={() => setIsEditing(true)}
                  size="sm"
                  variant="outline"
                >
                  Edit
                </Button>
              </div>
            </>
          )}
        </div>
        
        {/* Role */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Role
          </label>
          <p className="text-gray-900 capitalize">{user?.role}</p>
        </div>
        
        {/* Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Account Status
          </label>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            user?.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
          }`}>
            {user?.status}
          </span>
        </div>
        
        {/* Created Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Account Created
          </label>
          <p className="text-gray-900">{formatDate(user?.created_at)}</p>
        </div>
        
        {/* Updated Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Last Updated
          </label>
          <p className="text-gray-900">{formatDate(user?.updated_at)}</p>
        </div>
      </div>
    </div>
  );
};

export default ProfileInfo;
