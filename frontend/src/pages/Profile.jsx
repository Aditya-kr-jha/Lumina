import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ProfileInfo from '../components/profile/ProfileInfo';
import ChangePassword from '../components/profile/ChangePassword';
import UsageStats from '../components/profile/UsageStats';
import DeleteAccount from '../components/profile/DeleteAccount';
import Button from '../components/common/Button';

const Profile = () => {
  const navigate = useNavigate();
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <Button
            onClick={() => navigate('/dashboard')}
            variant="ghost"
            size="sm"
            className="mb-2"
          >
            <ArrowLeft size={18} />
            Back to Dashboard
          </Button>
          <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
        </div>
      </div>
      
      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        <ProfileInfo />
        <ChangePassword />
        <UsageStats />
        <DeleteAccount />
      </div>
    </div>
  );
};

export default Profile;
