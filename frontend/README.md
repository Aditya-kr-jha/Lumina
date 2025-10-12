<div align="center">

# ✨ Lumina

### AI-Powered Document Intelligence Platform

*Transform your PDFs into interactive conversations with cutting-edge AI technology*

[![React](https://img.shields.io/badge/React-19.1.1-61DAFB?logo=react)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-7.1.9-646CFF?logo=vite)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.1.14-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-Ready-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Features](#-features) • [Demo](#-demo) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🎯 Overview

**Lumina** is a modern, intelligent document analysis platform that leverages AI to help you extract insights, ask questions, and discover information from your PDF documents instantly. Built with React and powered by advanced language models, Lumina transforms static documents into interactive knowledge bases.

### Why Lumina?

- 🚀 **Instant Answers** - Get precise answers from your documents in seconds
- 🔒 **Privacy First** - Your documents stay secure and private
- 💡 **Smart Citations** - Every answer comes with source references
- 🎨 **Beautiful UI** - Modern, responsive design that works everywhere
- ⚡ **Lightning Fast** - Built on Vite for optimal performance

---

## ✨ Features

### 🔐 **Authentication & Security**
- Secure user registration and login system
- JWT-based authentication with auto-refresh
- Password strength validation with visual feedback
- Social login ready (Google, GitHub)
- Protected routes and role-based access
- Remember me functionality

### 📄 **Document Management**
- **Upload**: Drag-and-drop or click to upload PDFs
- **Processing**: Real-time status updates with visual indicators
- **Organization**: Search, filter, and manage multiple documents
- **Analytics**: Track document usage and query statistics
- **Batch Operations**: Upload and process multiple files at once
- **Smart Status**: Automatic polling for processing updates

### 💬 **AI Chat Interface**
- **Contextual Answers**: AI-powered responses based on document content
- **Source Citations**: See exactly where each answer comes from
- **Conversation History**: Browse and continue previous conversations
- **Example Questions**: Get started quickly with suggested prompts
- **Message Actions**: Regenerate, copy, or reference previous messages
- **Multi-Session**: Manage multiple chat sessions per document
- **Typing Indicators**: Real-time feedback during AI processing

### 👤 **User Profile & Settings**
- **Profile Management**: Edit personal information and preferences
- **Password Change**: Secure password update with validation
- **Usage Statistics**: Track your document and query usage
- **Account Control**: Safe account deletion with confirmation
- **Theme Support**: Light and dark mode ready

### 🎨 **Modern UI/UX**
- **Responsive Design**: Perfect on desktop, tablet, and mobile
- **Mobile Sidebar**: Collapsible hamburger menu for small screens
- **Gradient Backgrounds**: Beautiful purple → blue → cyan gradients
- **Smooth Animations**: 60fps transitions and micro-interactions
- **Toast Notifications**: Non-intrusive success/error messages
- **Loading States**: Skeleton loaders and spinners
- **Error Handling**: User-friendly error messages

---

## 🛠️ Tech Stack

### Core Technologies
- **[React 19.1.1](https://reactjs.org/)** - Modern UI library with latest features
- **[TypeScript](https://www.typescriptlang.org/)** - Type-safe JavaScript
- **[Vite 7.1.9](https://vitejs.dev/)** - Next-generation frontend tooling
- **[Tailwind CSS 4.1.14](https://tailwindcss.com/)** - Utility-first CSS framework

### State Management & Routing
- **React Context API** - Lightweight state management
- **React Router v7** - Client-side routing
- **Custom Hooks** - Reusable logic components

### UI & Icons
- **[Lucide React](https://lucide.dev/)** - Beautiful, consistent icons
- **Custom Components** - Fully styled, reusable components
- **CSS Animations** - Hardware-accelerated transitions

### HTTP & API
- **[Axios](https://axios-http.com/)** - Promise-based HTTP client
- **Interceptors** - Automatic token refresh
- **Error Handling** - Centralized API error management

### Development Tools
- **ESLint** - Code quality and consistency
- **PostCSS** - CSS processing and optimization
- **Autoprefixer** - Automatic vendor prefixing

---

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** 16.x or higher ([Download](https://nodejs.org/))
- **npm** 7.x or higher (comes with Node.js)
- **Backend API** - Lumina backend server running

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Aditya-kr-jha/Lumina-frontend.git
   cd Lumina-frontend/Lumina
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure the API endpoint**
   
   Edit `src/config/api.js` and update the API base URL:
   ```javascript
   export const API_BASE_URL = 'http://localhost:8000/api/v1';
   // Or your production URL:
   // export const API_BASE_URL = 'https://api.yourdomain.com/api/v1';
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   
   Navigate to **http://localhost:5173** (or the port shown in terminal)

---

## 📦 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Build optimized production bundle |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint to check code quality |

---

## 📁 Project Structure

```
Lumina/
│
├── 📂 public/                    # Static assets
│   └── vite.svg
│
├── 📂 src/                       # Source code
│   │
│   ├── 📂 assets/               # Images, fonts, static files
│   │
│   ├── 📂 components/           # React components
│   │   ├── 📂 auth/            # Authentication components
│   │   │   ├── LoginForm.jsx
│   │   │   ├── RegisterForm.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   │
│   │   ├── 📂 common/          # Reusable UI components
│   │   │   ├── Button.jsx
│   │   │   ├── Input.jsx
│   │   │   ├── Modal.jsx
│   │   │   ├── Toast.jsx
│   │   │   ├── Loader.jsx
│   │   │   ├── PasswordStrengthIndicator.jsx
│   │   │   └── SocialLoginButton.jsx
│   │   │
│   │   ├── 📂 dashboard/       # Dashboard components
│   │   │   ├── Sidebar.jsx
│   │   │   ├── ChatArea.jsx
│   │   │   ├── MessageList.jsx
│   │   │   ├── MessageInput.jsx
│   │   │   ├── Message.jsx
│   │   │   ├── DocumentList.jsx
│   │   │   ├── DocumentCard.jsx
│   │   │   ├── UploadArea.jsx
│   │   │   └── SourceCard.jsx
│   │   │
│   │   └── 📂 profile/         # Profile page components
│   │       ├── ProfileInfo.jsx
│   │       ├── ChangePassword.jsx
│   │       ├── UsageStats.jsx
│   │       └── DeleteAccount.jsx
│   │
│   ├── 📂 config/              # Configuration files
│   │   └── api.js              # API base URL & settings
│   │
│   ├── 📂 context/             # React Context providers
│   │   ├── AuthContext.jsx     # Authentication state
│   │   ├── ChatContext.jsx     # Chat state management
│   │   └── DocumentContext.jsx # Document state management
│   │
│   ├── 📂 pages/               # Page components (routes)
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   └── Profile.jsx
│   │
│   ├── 📂 services/            # API service layer
│   │   ├── api.js              # Axios instance & interceptors
│   │   ├── authService.js      # Authentication API calls
│   │   ├── chatService.js      # Chat API calls
│   │   └── documentService.js  # Document API calls
│   │
│   ├── 📂 utils/               # Utility functions
│   │   ├── constants.js        # App constants
│   │   ├── formatters.js       # Date, number formatters
│   │   └── validators.js       # Form validation helpers
│   │
│   ├── App.jsx                 # Main app component
│   ├── main.tsx                # Application entry point
│   └── index.css               # Global styles & Tailwind
│
├── .eslintrc.js                # ESLint configuration
├── postcss.config.js           # PostCSS configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite configuration
└── package.json                # Dependencies & scripts
```

### Key Directories Explained

**`components/`** - All React components organized by feature
- `auth/` - Login, registration, and route protection
- `common/` - Reusable UI elements used across the app
- `dashboard/` - Main dashboard interface components
- `profile/` - User profile and settings components

**`context/`** - Global state management using React Context API
- Manages authentication, chat sessions, and document data

**`services/`** - API communication layer
- Centralizes all backend API calls
- Includes request/response interceptors

**`pages/`** - Top-level route components
- Each file represents a unique page/route in the app

---

## 🎨 UI Features

### Recent Improvements (October 2025)

1. **Mobile Sidebar** 🎉
   - Collapsible hamburger menu on mobile
   - Smooth slide animations
   - Overlay backdrop with click-to-close
   - Auto-close after navigation

2. **Enhanced Authentication Pages** ✨
   - Vibrant gradient backgrounds
   - Rounded input fields (8px+ border radius)
   - Colorful feature badges
   - Friendly emoji accents
   - Decorative blur effects
   - Improved hover states

3. **Dashboard Gradient** 🌈
   - Beautiful purple → blue → cyan gradient
   - Maintains text readability
   - Modern, eye-catching design

See [FRONTEND_IMPROVEMENTS.md](./FRONTEND_IMPROVEMENTS.md) for detailed documentation.

---

## 🔧 Configuration

### API Configuration

Update `src/config/api.js`:

```javascript
// Development
export const API_BASE_URL = 'http://localhost:8000/api/v1';

// Request timeout
export const API_TIMEOUT = 30000; // 30 seconds
```

### Environment Variables (Optional)

Create a `.env` file in the root:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Lumina
VITE_ENABLE_ANALYTICS=false
```

---

## 🎯 Usage

### 1. Register an Account
- Visit the login page
- Click "Create one here 🚀"
- Fill in your details
- Accept terms and conditions
- Submit the form

### 2. Upload a Document
- Click "Upload PDF" in the sidebar
- Drag and drop or select a PDF file
- Wait for processing (status updates automatically)
- Document appears in the sidebar when ready

### 3. Start Chatting
- Select a document from the sidebar
- Type your question or click an example question
- Get instant AI-powered answers with citations
- Continue the conversation naturally

### 4. Manage Your Profile
- Click your profile icon in the sidebar
- Update personal information
- Change password securely
- View usage statistics

---

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

The optimized files will be in the `dist/` directory.

### Deploy to Popular Platforms

#### **Vercel** (Recommended)
```bash
npm i -g vercel
vercel
```

#### **Netlify**
```bash
npm run build
# Drag and drop the 'dist' folder to Netlify
```

#### **GitHub Pages**
```bash
npm run build
# Use gh-pages or GitHub Actions
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style
- Write meaningful commit messages
- Add comments for complex logic
- Test thoroughly before submitting
- Update documentation as needed

---

## 📝 Documentation

- [Project Summary](./PROJECT_SUMMARY.md) - High-level overview
- [Features](./FEATURES.md) - Detailed feature list
- [Setup Guide](./SETUP.md) - Installation and configuration
- [Frontend Improvements](./FRONTEND_IMPROVEMENTS.md) - Recent UI enhancements

---

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Kill the process using the port
lsof -ti:5173 | xargs kill -9
```

**API connection errors:**
- Verify backend server is running
- Check API_BASE_URL in `src/config/api.js`
- Ensure CORS is configured on backend

**Build errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Tailwind styles not working:**
- Verify Tailwind CSS v4 configuration
- Check PostCSS plugin: `@tailwindcss/postcss`
- Ensure `@import "tailwindcss"` is in index.css

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Aditya Kumar Jha** - [@Aditya-kr-jha](https://github.com/Aditya-kr-jha)

---

## 🙏 Acknowledgments

- [React](https://reactjs.org/) - UI framework
- [Vite](https://vitejs.dev/) - Build tool
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [Lucide](https://lucide.dev/) - Icons
- [Axios](https://axios-http.com/) - HTTP client

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐️ on GitHub!

---

<div align="center">

**Built with ❤️ using React and Tailwind CSS**

[Report Bug](https://github.com/Aditya-kr-jha/Lumina-frontend/issues) • [Request Feature](https://github.com/Aditya-kr-jha/Lumina-frontend/issues) • [Documentation](./docs)

</div>
