# Frontend - LottoAI React Application

This directory contains the React frontend application built with Vite, providing a modern, responsive user interface for the LottoAI lottery verification system.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Components](#components)
- [State Management](#state-management)
- [Routing & Navigation](#routing--navigation)
- [Styling Approach](#styling-approach)
- [API Integration](#api-integration)
- [Development](#development)
- [Build & Deployment](#build--deployment)

---

## 🎯 Overview

The frontend is a single-page application (SPA) built with **React 19** and **Vite**. It provides:

- **Responsive design** optimized for desktop and mobile
- **Modern UI/UX** with smooth animations (Framer Motion)
- **Modal-based forms** for authentication and uploads
- **Global state management** using React Context API
- **Secure authentication** with JWT tokens stored in localStorage

**Key Features:**
- Instant ticket verification with real-time feedback
- Smooth transitions and micro-interactions
- Accessible design following WCAG guidelines
- SEO-friendly structure

---

## 🛠️ Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.2.0 | UI library |
| **Vite** | 7.2.2 | Build tool & dev server |
| **Styled Components** | 6.1.19 | CSS-in-JS for component styling |
| **Framer Motion** | 12.23.24 | Animation library |
| **Axios** | 1.13.2 | HTTP client for API calls |
| **Tailwind CSS** | 3.4.1 | Utility-first CSS framework |
| **Canvas Confetti** | 1.9.4 | Celebration effects for winners |

### Why These Choices?

**React 19:**
- Latest stable version with improved performance
- Server Components support (future enhancement)
- Enhanced hooks and concurrent features

**Vite:**
- Lightning-fast dev server with HMR (Hot Module Replacement)
- Optimized production builds
- Native ESM support

**Styled Components:**
- Component-scoped styles
- Dynamic styling based on props
- No naming conflicts
- Better than plain CSS for maintainability

**Framer Motion:**
- Declarative animations
- Smooth transitions with spring physics
- Gesture support

---

## 📁 Project Structure

```
frontend/
├── public/                     # Static assets
│   ├── background_image/       # Background patterns
│   │   ├── blue_and_gold_marble.jpg
│   │   └── gold_and_navy_marble.jpg
│   └── icon/                   # Favicon files
│       └── favicon_io/
│
├── src/                        # Source code
│   ├── components/             # React components
│   │   ├── AnimatedArrow.jsx   # Animated arrow for process flow
│   │   ├── Button-ChangeColor.jsx  # Interactive button component
│   │   ├── Button-Modern.jsx   # Modern style button
│   │   ├── CenterCard.jsx      # Central hero card
│   │   ├── Form-SignIn.jsx     # Sign in modal form
│   │   ├── Form-SignUp.jsx     # Sign up modal form
│   │   ├── Form-UploadImage.jsx # Image upload modal
│   │   ├── LightRays.jsx       # Background light effect
│   │   ├── Navbar.jsx          # Top navigation bar
│   │   ├── ProcessBox.jsx      # Process step indicator
│   │   └── Text-Underline.jsx  # Animated underline text
│   │
│   ├── contexts/               # React Context providers
│   │   └── AuthContext.jsx     # Authentication state management
│   │
│   ├── hooks/                  # Custom React hooks
│   │   └── useAuth.js          # Hook to access auth context
│   │
│   ├── assets/                 # Images, fonts, etc.
│   ├── sections/               # Page sections (future)
│   ├── utils/                  # Utility functions (future)
│   │
│   ├── App.jsx                 # Main application component
│   ├── main.jsx                # Application entry point
│   └── index.css               # Global styles
│
├── index.html                  # HTML entry point
├── vite.config.js              # Vite configuration
├── tailwind.config.js          # Tailwind configuration
├── postcss.config.js           # PostCSS configuration
├── eslint.config.js            # ESLint configuration
└── package.json                # Dependencies & scripts
```

---

## 🧩 Components

### Core Components

#### `App.jsx` - Main Application

**Purpose:** Root component that orchestrates the entire UI.

**Key Features:**
- Manages modal states (SignIn, SignUp, Upload)
- Implements animation sequence for process flow
- Handles scroll interactions
- Wraps app with AuthProvider

**State Management:**
```jsx
const [isSignInOpen, setIsSignInOpen] = useState(false);
const [isSignUpOpen, setIsSignUpOpen] = useState(false);
const [isModalOpen, setIsModalOpen] = useState(false);
const [showBoxes, setShowBoxes] = useState(false);
```

**Sections:**
1. **Hero Section:** Central card with "Try It Now" button
2. **Process Flow:** Animated boxes showing Upload → Detection → Extract → Analyze
3. **Modals:** SignIn, SignUp, and Upload forms

---

#### `Navbar.jsx` - Navigation Bar

**Features:**
- Shows "Sign In" button when logged out
- Shows username + "Logout" button when logged in
- Hover effect with mouse-following gradient
- Sticky positioning

---

### Form Components

#### `Form-SignIn.jsx` - Sign In Modal

**Features:**
- Email + password login
- Google OAuth button
- Switch to sign-up link
- Error handling with user feedback
- Loading states

---

#### `Form-SignUp.jsx` - Sign Up Modal

**Features:**
- Email + username + password registration
- Password strength indicator (future enhancement)
- Google OAuth button
- Terms & conditions checkbox
- Switch to sign-in link

**Validation:**
- Email format validation
- Password minimum length (8 characters)
- Username uniqueness (server-side)

---

#### `Form-UploadImage.jsx` - Upload Modal

**Features:**
- Drag & drop file upload
- File preview before upload
- Progress indicator
- Real-time results display
- Prize tier visualization
- Debug mode toggle

---

### UI Components

#### `CenterCard.jsx` - Hero Card

**Purpose:** Main call-to-action in the center of the landing page.

**Features:**
- Framer Motion entrance animation
- Hover effects
- "Try It Now" button
- Tagline and description

---

#### `ProcessBox.jsx` - Process Step Indicator

**Props:**
```jsx
{
  icon: string,           // Emoji or icon
  title: string,          // Step title
  description: string,    // Step description
  delay: number,          // Animation delay
  controls: object        // Framer Motion controls
}
```

**Animation:**
```jsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  animate={controls}
  transition={{ duration: 0.6, delay }}
>
  {/* Content */}
</motion.div>
```

---

#### `AnimatedArrow.jsx` - Directional Arrow

**Purpose:** Connects process boxes to show flow direction.

---

#### `LightRays.jsx` - Background Effect

**Purpose:** Animated light rays emanating from center.

**Implementation:** CSS animations with styled-components.

---

### Utility Components

#### `Button-ChangeColor.jsx` - Interactive Button

**Features:**
- Color change on hover
- Smooth transitions
- Customizable via props

---

#### `Button-Modern.jsx` - Modern Button

**Features:**
- Glassmorphism effect
- Shadow on hover
- Ripple effect on click

---

#### `Text-Underline.jsx` - Animated Underline

**Purpose:** Text with animated underline effect on hover.

---

## 🔄 State Management

### AuthContext - Global Authentication State

**Location:** `src/contexts/AuthContext.jsx`

**Purpose:** Centralized authentication state accessible throughout the app.

**Provides:**
```jsx
{
  user: object | null,              // Current user info
  token: string | null,             // JWT token
  loading: boolean,                 // Loading state during auth ops
  login: (email, password) => void, // Login function
  signup: (email, username, password) => void,  // Signup function
  logout: () => void,               // Logout function
  googleLogin: () => void           // Google OAuth function
}
```
---

### useAuth Hook - Convenient Access

**Location:** `src/hooks/useAuth.js`

---

## 🧭 Routing & Navigation

### Current Structure (Single Page)

The app currently uses **modal-based navigation** rather than traditional routing:

- **Landing page:** Always visible
- **Modals:**
  - Sign In
  - Sign Up
  - Upload Image

---

## 🔨 Development

### Running Dev Server

```bash
# From frontend directory
npm run dev

# Or from project root
npm run dev:frontend
```

Dev server runs on: http://localhost:5173

### Hot Module Replacement (HMR)

Vite provides instant HMR - changes appear immediately without full page reload.

---

**Built with React ⚛️ & Vite ⚡**
