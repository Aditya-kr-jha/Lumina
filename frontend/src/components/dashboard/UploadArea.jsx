import { useCallback, useState } from 'react';
import { Upload, CloudUpload } from 'lucide-react';
import { useDocuments } from '../../context/DocumentContext';
import { showToast } from '../common/Toast';
import { validateFile } from '../../utils/validators';
import { FILE_SIZE_LIMITS } from '../../utils/constants';

const UploadArea = () => {
  const { uploadSingleDocument, uploadMultiple, uploadProgress } = useDocuments();
  const [isDragOver, setIsDragOver] = useState(false);
  
  const handleFileUpload = useCallback(async (files) => {
    const fileArray = Array.from(files);
    
    console.log('Files to upload:', fileArray); // DEBUG
    
    // Validate all files first
    for (const file of fileArray) {
      const error = validateFile(file);
      if (error) {
        showToast(error, 'error');
        return;
      }
    }
    
    if (fileArray.length === 1) {
      console.log('Uploading single document:', fileArray[0].name); // DEBUG
      const result = await uploadSingleDocument(fileArray[0]);
      
      console.log('Upload result:', result); // DEBUG
      
      if (result.success) {
        showToast('Document uploaded successfully', 'success');
      } else {
        showToast(result.error || 'Upload failed', 'error');
      }
    } else {
      console.log('Uploading multiple documents:', fileArray.length); // DEBUG
      const result = await uploadMultiple(fileArray);
      
      console.log('Batch upload result:', result); // DEBUG
      
      if (result.success) {
        const { success, failed } = result.data;
        showToast(
          `${success} document(s) uploaded successfully${failed > 0 ? `, ${failed} failed` : ''}`,
          failed > 0 ? 'warning' : 'success'
        );
      } else {
        showToast(result.error || 'Upload failed', 'error');
      }
    }
  }, [uploadSingleDocument, uploadMultiple]); // Add dependencies
  
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    
    console.log('Drop event triggered'); // DEBUG
    
    const files = e.dataTransfer.files;
    console.log('Dropped files:', files); // DEBUG
    
    if (files.length > 0) {
      handleFileUpload(files);
    }
  }, [handleFileUpload]); // Add handleFileUpload as dependency
  
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);
  
  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);
  
  const handleFileSelect = useCallback((e) => {
    console.log('File select triggered'); // DEBUG
    
    const files = e.target.files;
    console.log('Selected files:', files); // DEBUG
    
    if (files.length > 0) {
      handleFileUpload(files);
    }
    
    // Reset input value to allow selecting the same file again
    e.target.value = '';
  }, [handleFileUpload]); // Add handleFileUpload as dependency
  
  const handleClick = useCallback(() => {
    console.log('Upload area clicked'); // DEBUG
    document.getElementById('file-upload').click();
  }, []);
  
  const hasActiveUploads = Object.keys(uploadProgress).length > 0;
  
  return (
    <div className="p-4">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        aria-label="Upload PDF documents by clicking or dragging and dropping"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleClick();
          }
        }}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 ${
          isDragOver
            ? 'border-purple-500 bg-purple-50 scale-[1.02] shadow-lg'
            : 'border-gray-300 hover:border-purple-400 hover:bg-purple-25 bg-white'
        }`}
      >
        <input
          id="file-upload"
          type="file"
          multiple
          accept={FILE_SIZE_LIMITS.ACCEPTED_FORMATS.join(',')}
          onChange={handleFileSelect}
          className="hidden"
        />
        
        {hasActiveUploads ? (
          <div className="space-y-4">
            <CloudUpload className="mx-auto text-purple-600 animate-bounce" size={48} />
            {Object.entries(uploadProgress).map(([filename, progress]) => (
              <div key={filename} className="text-sm">
                <p className="text-gray-700 truncate font-medium">{filename}</p>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">{progress}% complete</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <CloudUpload 
              className={`mx-auto transition-colors ${isDragOver ? 'text-purple-600' : 'text-gray-400'}`} 
              size={56} 
            />
            <div className="space-y-1">
              <p className={`text-sm font-medium transition-colors ${
                isDragOver ? 'text-purple-600' : 'text-gray-700'
              }`}>
                Drag & drop PDFs here, or click to browse
              </p>
              <p className="text-xs text-gray-500">
                Maximum file size: 10MB
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadArea;