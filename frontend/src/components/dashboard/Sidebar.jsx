import { useState } from 'react';
import { Plus, Search, FileText, LogOut, User, ChevronDown, X } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useChat } from '../../context/ChatContext';
import { useDocuments } from '../../context/DocumentContext';
import DocumentList from './DocumentList';
import UploadArea from './UploadArea';
import { useNavigate } from 'react-router-dom';

const Sidebar = ({ isOpen, onClose }) => {
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const { user, logout } = useAuth();
  const { startNewChat } = useChat();
  const { setCurrentDocument } = useDocuments();
  const navigate = useNavigate();
  
  const handleNewChat = () => {
    startNewChat();
    setCurrentDocument(null);
    onClose && onClose(); // Close sidebar on mobile after action
  };
  
  const handleLogout = () => {
    logout();
  };
  
  const handleProfile = () => {
    navigate('/profile');
    setShowProfileMenu(false);
    onClose && onClose(); // Close sidebar on mobile after action
  };
  
  const getUserInitial = () => {
    return user?.username?.charAt(0).toUpperCase() || 'U';
  };
  
  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden transition-opacity"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <div className={`
        fixed lg:relative inset-y-0 left-0 z-50 
        w-80 bg-gray-100 border-r border-gray-200 flex flex-col h-full
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
      {/* Section 1: Header (Top - Fixed) */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
            <FileText className="text-white" size={20} />
          </div>
          <h1 className="text-xl font-bold text-gray-900 flex-1">Lumina</h1>
          {/* Close button for mobile */}
          <button
            onClick={onClose}
            className="lg:hidden p-2 hover:bg-gray-200 rounded-lg transition-colors"
            aria-label="Close sidebar"
          >
            <X size={20} className="text-gray-600" />
          </button>
        </div>
        
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:border-purple-500 transition-colors"
        >
          <Plus size={18} />
          New Chat
        </button>
      </div>
      
      {/* Section 2: Search Bar (Below Header - Fixed) */}
      <div className="p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
      </div>
      
      {/* Section 3: Document List (Middle - Scrollable) */}
      <div className="flex-1 overflow-y-auto px-4 pb-4">
        <DocumentList searchQuery={searchQuery} />
      </div>
      
      {/* Section 4: Upload Area (Bottom - Fixed) */}
      <div className="border-t border-gray-200">
        <UploadArea />
      </div>
      
      {/* Profile Section */}
      <div className="p-4 border-t border-gray-200 relative">
        <button
          onClick={() => setShowProfileMenu(!showProfileMenu)}
          className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <div className="w-10 h-10 rounded-full bg-purple-600 text-white flex items-center justify-center font-semibold">
            {getUserInitial()}
          </div>
          <div className="flex-1 text-left">
            <p className="text-sm font-medium text-gray-900">{user?.username}</p>
            <p className="text-xs text-gray-500">{user?.email}</p>
          </div>
          <ChevronDown className="text-gray-400" size={20} />
        </button>
        
        {/* Profile Dropdown */}
        {showProfileMenu && (
          <div className="absolute bottom-full left-4 right-4 mb-2 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden">
            <button
              onClick={handleProfile}
              className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-100 transition-colors text-left"
            >
              <User size={18} className="text-gray-600" />
              <span className="text-sm text-gray-900">Profile Settings</span>
            </button>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-100 transition-colors text-left border-t"
            >
              <LogOut size={18} className="text-red-600" />
              <span className="text-sm text-red-600">Logout</span>
            </button>
          </div>
        )}
      </div>
      </div>
    </>
  );
};

export default Sidebar;
