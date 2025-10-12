import { useState } from 'react';
import { FileText, ExternalLink } from 'lucide-react';

const SourceCard = ({ source, index, onClick }) => {
  const relevancePercentage = Math.round(source.similarity_score * 100);
  
  const getRelevanceColor = (score) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-blue-600 bg-blue-100';
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };
  
  const handleClick = () => {
    if (onClick) {
      onClick(source);
    }
  };
  
  return (
    <button
      onClick={handleClick}
      className="flex flex-col items-start gap-2 p-3 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-purple-400 hover:shadow-sm transition-all duration-200 cursor-pointer text-left w-full min-w-[120px] max-w-[140px]"
      role="button"
      aria-label={`Source reference, Page ${source.page_number}, ${relevancePercentage}% relevant`}
    >
      {/* Page Reference */}
      <div className="flex items-center gap-2 w-full">
        <FileText className="text-gray-500 flex-shrink-0" size={14} />
        <span className="text-sm font-medium text-gray-900 truncate">
          Page {source.page_number}
        </span>
        <ExternalLink className="text-gray-400 flex-shrink-0 ml-auto" size={12} />
      </div>
      
      {/* Relevance Score */}
      <div className="w-full">
        <span
          className={`text-xs px-2 py-1 rounded-full font-medium ${getRelevanceColor(source.similarity_score)}`}
        >
          {relevancePercentage}% relevant
        </span>
      </div>
    </button>
  );
};

export default SourceCard;
