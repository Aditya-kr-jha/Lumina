import { useState } from 'react';
import { AlertTriangle } from 'lucide-react';
import { deleteAccount } from '../../services/authService';
import { useAuth } from '../../context/AuthContext';
import Button from '../common/Button';
import Modal from '../common/Modal';
import Input from '../common/Input';
import { showToast } from '../common/Toast';

const DeleteAccount = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [confirmText, setConfirmText] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { logout } = useAuth();
  
  const handleDelete = async () => {
    if (confirmText !== 'DELETE') {
      showToast('Please type DELETE to confirm', 'error');
      return;
    }
    
    if (!password) {
      showToast('Please enter your password', 'error');
      return;
    }
    
    setIsLoading(true);
    
    try {
      await deleteAccount();
      showToast('Account deleted successfully', 'success');
      
      // Logout and redirect
      setTimeout(() => {
        logout();
      }, 1000);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete account';
      showToast(errorMessage, 'error');
      setIsLoading(false);
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow p-6 border-2 border-red-200">
      <div className="flex items-start gap-3 mb-4">
        <AlertTriangle className="text-red-600 flex-shrink-0" size={24} />
        <div>
          <h2 className="text-xl font-semibold text-red-900 mb-2">Danger Zone</h2>
          <p className="text-sm text-gray-700">
            Once you delete your account, there is no going back. This will permanently delete your
            account, all your documents, and all conversation history. This action cannot be undone.
          </p>
        </div>
      </div>
      
      <Button
        variant="danger"
        onClick={() => setIsModalOpen(true)}
      >
        Delete Account
      </Button>
      
      {/* Confirmation Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          if (!isLoading) {
            setIsModalOpen(false);
            setConfirmText('');
            setPassword('');
          }
        }}
        title="Delete Account"
        size="md"
      >
        <div className="space-y-4">
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800 font-medium">
              ⚠️ This action is permanent and cannot be undone!
            </p>
          </div>
          
          <p className="text-sm text-gray-700">
            This will permanently delete your account and all associated data, including:
          </p>
          
          <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
            <li>All uploaded documents</li>
            <li>All conversation history</li>
            <li>All personal information</li>
          </ul>
          
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type <span className="font-bold">DELETE</span> to confirm
              </label>
              <Input
                type="text"
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                placeholder="DELETE"
              />
            </div>
            
            <Input
              label="Enter your password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              showPasswordToggle
            />
          </div>
          
          <div className="flex gap-3 justify-end pt-4">
            <Button
              variant="secondary"
              onClick={() => {
                setIsModalOpen(false);
                setConfirmText('');
                setPassword('');
              }}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleDelete}
              loading={isLoading}
              disabled={isLoading || confirmText !== 'DELETE' || !password}
            >
              Delete My Account
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default DeleteAccount;
