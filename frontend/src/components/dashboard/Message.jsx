import { User, Bot, Copy, RotateCw } from 'lucide-react';
import SourceCard from './SourceCard';
import { formatProcessingTime } from '../../utils/formatters';
import { showToast } from '../common/Toast';

const Message = ({ message, onRegenerate, isLast }) => {
  const isUser = message.role === 'user';
  
  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    showToast('Copied to clipboard', 'success');
  };
  
  return (
    <div className={`flex gap-4 mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="flex-shrink-0 w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center shadow-md">
          <Bot className="text-white" size={18} />
        </div>
      )}
      
      <div className={`flex-1 max-w-[80%] sm:max-w-[70%] ${isUser ? 'flex justify-end' : ''}`}>
        <div className={`inline-block max-w-full ${
          isUser 
            ? 'bg-gradient-to-br from-purple-600 to-purple-700 text-white rounded-2xl rounded-tr-sm px-4 py-3 shadow-md' 
            : 'bg-gray-100 text-gray-900 rounded-2xl rounded-tl-sm px-4 py-3 border border-gray-200'
        }`}>
          <p className="text-[15px] leading-relaxed whitespace-pre-wrap break-words">{message.content}</p>
          
          {/* Sources */}
          {!isUser && message.sources && message.sources.length > 0 && (
            <div className="mt-4 space-y-2">
              <p className="text-xs font-semibold text-gray-600 mb-2">Sources:</p>
              {message.sources.map((source, index) => (
                <SourceCard key={source.chunk_id} source={source} index={index} />
              ))}
            </div>
          )}
          
          {/* Processing Time */}
          {!isUser && message.processing_time && (
            <p className="text-xs text-gray-500 mt-3 pt-2 border-t border-gray-200">
              Responded in {formatProcessingTime(message.processing_time)}
            </p>
          )}
          
          {/* Actions */}
          {!isUser && (
            <div className="flex items-center gap-3 mt-3 pt-3 border-t border-gray-200">
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 text-xs text-gray-600 hover:text-gray-900 transition-colors"
              >
                <Copy size={14} />
                Copy
              </button>
              
              {isLast && onRegenerate && (
                <button
                  onClick={onRegenerate}
                  className="flex items-center gap-1 text-xs text-gray-600 hover:text-gray-900 transition-colors"
                >
                  <RotateCw size={14} />
                  Regenerate
                </button>
              )}
            </div>
          )}
        </div>
      </div>
      
      {isUser && (
        <div className="flex-shrink-0 w-9 h-9 rounded-full bg-gray-300 flex items-center justify-center shadow-sm">
          <User className="text-gray-700" size={18} />
        </div>
      )}
    </div>
  );
};

export default Message;
