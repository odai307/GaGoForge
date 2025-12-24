# Framework Challenge Platform - Frontend

A LeetCode-style learning platform focused on framework-specific scenario challenges. Users solve real-world framework implementation challenges and receive instant feedback through static code analysis.

## 🚀 Features

- **Browse Problems** by framework, category, and difficulty
- **Solve Challenges** in an integrated code editor
- **Instant Validation** with detailed feedback
- **Track Progress** across frameworks and difficulties
- **User Profiles** with stats and streaks

## 🛠 Tech Stack

- **Frontend Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Routing**: React Router v6
- **State Management**: Zustand
- **HTTP Client**: Axios
- **UI Framework**: Tailwind CSS
- **Code Editor**: Monaco Editor
- **Deployment**: Vercel/Netlify

## 📋 Prerequisites

- Node.js 16 or higher
- npm or yarn
- Git

## 🏗 Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd GaGoForge/client


2. Install Dependencies
bash
npm install
3. Environment Configuration
Create a .env file in the client directory:

env
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=FrameworkChallenge
VITE_APP_VERSION=1.0.0
4. Start Development Server
bash
npm run dev
The application will be available at http://localhost:5173

📁 Project Structure
text
client/src/
├── components/              # Reusable UI components
│   ├── layout/             # Layout components
│   │   ├── Header.jsx
│   │   ├── Footer.jsx
│   │   └── Layout.jsx
│   └── common/             # Common UI components
├── contexts/               # React contexts
│   └── AuthContext.jsx     # Authentication context
├── pages/                  # Route components
│   ├── Home.jsx            # Landing page
│   ├── ProblemsList.jsx    # Problem browsing
│   ├── ProblemDetail.jsx   # Problem solving interface
│   ├── Profile.jsx         # User profile
│   ├── UserProfile.jsx     # Extended profile view
│   ├── Login.jsx           # Authentication
│   ├── Register.jsx        # User registration
│   ├── Leaderboard.jsx     # Rankings (future)
│   └── NotFound.jsx        # 404 page
├── services/               # API communication layer
│   ├── api.js              # Axios configuration
│   ├── auth.js             # Authentication services
│   ├── problems.js         # Problem data services
│   ├── submissions.js      # Submission handling
│   └── progress.js         # User progress tracking
├── utils/                  # Utility functions
│   └── token.js            # Token management
├── App.jsx                 # Main app component
├── App.css                 # Global styles
├── main.jsx                # App entry point
└── index.css               # Base styles
🎯 Available Scripts
npm run dev - Start development server

npm run build - Build for production

npm run preview - Preview production build

npm run lint - Run ESLint

npm run test - Run tests (when configured)

🔌 Backend Integration
API Endpoints
The frontend expects the backend to be running at http://localhost:8000 with these endpoints:

Authentication
POST /api/auth/register/ - User registration

POST /api/auth/login/ - User login (returns JWT)

POST /api/auth/logout/ - User logout

GET /api/auth/me/ - Get current user info

Problems
GET /api/frameworks/ - List all frameworks

GET /api/problems/ - List problems (filterable)

GET /api/problems/{id}/ - Get problem details

Submissions
POST /api/submissions/ - Submit code for validation

GET /api/submissions/{id}/ - Get submission details

GET /api/submissions/ - List user's submissions

User Progress
GET /api/users/me/profile/ - Get user profile & stats

GET /api/users/me/progress/ - Get progress for all problems

GET /api/users/me/submissions/ - Get submission history

Authentication Flow
User logs in via /api/auth/login/

JWT token is stored in localStorage

Token is automatically included in all API requests via Axios interceptors

On 401 responses, user is redirected to login page

🎨 UI Components
Layout Components
Header: Navigation bar with user menu

Footer: Site information and links

Layout: Main app layout wrapper

Page Components
Home: Overview with featured problems and quick stats

ProblemsList: Filterable problem table with search

ProblemDetail: Main solving interface with code editor

Profile: User statistics and progress tracking

Planned Components
CodeEditor (Monaco Editor integration)

Progress charts and visualizations

Submission feedback panel

Hint system

🔧 Development
Adding New Features
Create component in appropriate directory

Add route in App.jsx if needed

Create API service if required

Update TypeScript types

Test integration

State Management
Using Zustand for simple state management:

javascript
// Example store
import { create } from 'zustand';

const useAuthStore = create((set) => ({
  user: null,
  token: null,
  login: (userData) => set({ user: userData.user, token: userData.token }),
  logout: () => set({ user: null, token: null }),
}));
API Service Pattern
javascript
// services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
🚀 Deployment
Vercel Deployment
Build the project:

bash
npm run build
Deploy to Vercel:

bash
npm install -g vercel
vercel --prod
Environment variables: Set in Vercel dashboard:

VITE_API_URL: Your production backend URL

VITE_APP_NAME: Your app name

Netlify Deployment
Build command: npm run build

Publish directory: dist

Environment variables: Set in Netlify dashboard

🐛 Troubleshooting
Common Issues
CORS Errors

Ensure backend has CORS configured for frontend domain

Check VITE_API_URL environment variable

Authentication Issues

Verify token is being stored in localStorage

Check backend authentication endpoints

Build Failures

Clear node_modules and reinstall: rm -rf node_modules && npm install

Check for TypeScript errors

API Connection

Verify backend server is running

Check network tab in browser dev tools

Development Tips
Use React Developer Tools for debugging

Check Network tab for API request/response inspection

Monitor Console for JavaScript errors

Use React Query for advanced API state management (optional)

📈 Future Enhancements
Real-time code collaboration

Advanced code editor features (autocomplete, snippets)

Social features (following, sharing solutions)

Mobile app (React Native)

Offline solving capability

Integration with popular IDEs

🤝 Contributing
Fork the repository

Create a feature branch: git checkout -b feature/amazing-feature

Commit changes: git commit -m 'Add amazing feature'

Push to branch: git push origin feature/amazing-feature

Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🆘 Support
For technical support:

Check the API Documentation

Review browser console for errors

Check network requests in dev tools

Contact backend team for API-related issues

Happy coding! 🎉

text

Save this as `client/README.md` in your frontend directory. This provides comprehensive documentation for setting up, developing, and deploying your frontend application.
