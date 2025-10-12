# Quick Setup Guide

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure API Endpoint**
   
   Edit `src/config/api.js`:
   ```javascript
   export const API_BASE_URL = 'http://your-backend-domain.com/api/v1';
   ```
   
   Or create a `.env` file:
   ```env
   VITE_API_BASE_URL=http://your-backend-domain.com/api/v1
   ```

3. **Run Development Server**
   ```bash
   npm run dev
   ```
   
   Open http://localhost:5173

## 📁 Project Overview

### Key Directories

- **`src/components/`** - All UI components
  - `auth/` - Login, Register, Protected Routes
  - `dashboard/` - Main app interface components
  - `profile/` - User profile components
  - `common/` - Reusable components (Button, Input, Modal, etc.)

- **`src/context/`** - React Context providers
  - `AuthContext` - User authentication state
  - `DocumentContext` - Document management state
  - `ChatContext` - Chat/messaging state

- **`src/services/`** - API service layer
  - `authService.js` - Authentication APIs
  - `documentService.js` - Document management APIs
  - `chatService.js` - Chat/query APIs

- **`src/utils/`** - Helper functions
  - `constants.js` - App-wide constants
  - `formatters.js` - Data formatting utilities
  - `validators.js` - Form validation functions

- **`src/pages/`** - Page components
  - `Login.jsx` - Login page
  - `Register.jsx` - Registration page
  - `Dashboard.jsx` - Main dashboard
  - `Profile.jsx` - User profile page

### Routes

| Route | Access | Description |
|-------|--------|-------------|
| `/` | Public | Login page |
| `/register` | Public | Registration page |
| `/dashboard` | Protected | Main application interface |
| `/profile` | Protected | User profile and settings |

## 🔧 Configuration Options

### API Endpoints (src/config/api.js)

The app expects these backend endpoints:

**Authentication:**
- POST `/token` - Login
- POST `/user/register` - Register
- GET `/user/me` - Get profile
- PATCH `/user/me` - Update profile
- POST `/user/me/change-password` - Change password
- DELETE `/user/me` - Delete account

**Documents:**
- GET `/documents/` - List documents
- POST `/documents/upload` - Upload PDF
- POST `/documents/batch-upload` - Upload multiple PDFs
- GET `/documents/{id}` - Get document details
- GET `/documents/{id}/status` - Get processing status
- DELETE `/documents/{id}` - Delete document

**Chat:**
- POST `/chat/query` - Send question
- GET `/chat/sessions` - List sessions
- GET `/chat/history/{session_id}` - Get chat history
- DELETE `/chat/session/{session_id}` - Delete session
- DELETE `/chat/sessions/clear-all` - Clear all sessions
- GET `/chat/stats/queries` - Get user stats
- GET `/chat/stats/document/{id}` - Get document stats

### Constants (src/utils/constants.js)

Customize app behavior:

```javascript
export const FILE_SIZE_LIMITS = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ACCEPTED_FORMATS: ['.pdf'],
};

export const CHAT_CONFIG = {
  DEFAULT_TOP_K: 4, // Number of source chunks
  POLLING_INTERVAL: 2000, // Status polling (ms)
};

export const EXAMPLE_QUESTIONS = [
  "What is this document about?",
  // Add your own examples...
];
```

### Styling (tailwind.config.js)

Customize colors:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        50: '#f0f9ff',
        // ... customize your primary color
      }
    }
  }
}
```

## 🔑 Key Features

### Authentication Flow
1. User registers/logs in
2. JWT token stored in localStorage
3. Token included in all API requests
4. Auto-logout on 401 response

### Document Upload
1. Select PDF file(s)
2. Files validated (size, type)
3. Uploaded to backend
4. Status polled every 2s until ready
5. Visual indicators show processing state

### Chat Flow
1. Select a document
2. New session ID generated
3. Ask questions about the document
4. Receive AI answers with source citations
5. Follow-up questions use same session

### Session Management
- Each conversation has unique session ID
- Sessions persist across page refreshes
- Can load previous chat history
- Can clear individual or all sessions

## 🐛 Troubleshooting

### Build Errors

**Tailwind not working:**
```bash
npm install -D @tailwindcss/postcss autoprefixer
```

**TypeScript errors:**
Already configured with `allowJs: true` in tsconfig.json

### Runtime Issues

**CORS errors:**
Ensure backend allows requests from `http://localhost:5173`

**API connection failed:**
Check API_BASE_URL in `src/config/api.js`

**Login fails:**
Verify backend is running and credentials are correct

**Documents not loading:**
Check browser console for API errors

## 📦 Build & Deploy

### Production Build
```bash
npm run build
```

Output: `dist/` directory

### Preview Build
```bash
npm run preview
```

### Deploy
Deploy the `dist/` folder to any static hosting:
- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- etc.

## 🧪 Testing

The application is ready to test with your backend API. Key test scenarios:

1. **Registration & Login**
   - Create new account
   - Login with credentials
   - Invalid credentials handling

2. **Document Management**
   - Upload single PDF
   - Upload multiple PDFs
   - Delete documents
   - Document search

3. **Chat Functionality**
   - Ask questions
   - View sources
   - Regenerate responses
   - Multiple sessions

4. **Profile Management**
   - Update email
   - Change password
   - View statistics
   - Delete account

## 📝 Next Steps

1. Update `API_BASE_URL` with your backend URL
2. Customize branding (logo, colors, name)
3. Add custom example questions
4. Adjust file size limits if needed
5. Test all features with your backend
6. Deploy to production

## 🤝 Support

For issues or questions:
1. Check browser console for errors
2. Verify API endpoints are accessible
3. Ensure backend is running correctly
4. Check network tab for failed requests

Happy coding! 🎉
