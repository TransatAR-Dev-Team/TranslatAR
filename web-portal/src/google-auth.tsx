/**
 * Google Authentication Component
 * 
 * This component integrates with Google Identity Services (GIS) to enable
 * client-side OAuth flow. Reference: https://github.com/ekourtakis/RetroInsta
 * 
 * How it works:
 * 1. User clicks "Sign in with Google" button
 * 2. Google popup appears (handled by Google Identity Services library)
 * 3. User authenticates with Google
 * 4. Google returns an ID Token (JWT)
 * 5. Frontend sends ID Token to backend /api/auth/google/login
 * 6. Backend verifies token and returns application JWT
 * 7. Store JWT in localStorage/sessionStorage
 */

import { useEffect, useState } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  picture: string;
}

interface GoogleLoginResponse {
  token: string;
  user: User;
}

declare global {
  interface Window {
    google?: any;
  }
}

export function useGoogleAuth() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // Load Google Identity Services script
    if (typeof window.google === 'undefined') {
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = () => setIsLoaded(true);
      document.body.appendChild(script);
    } else {
      setIsLoaded(true);
    }

    // Check for existing token in localStorage
    const storedToken = localStorage.getItem('jwt_token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleCredentialResponse = async (response: any) => {
    try {
      // Send ID Token to backend
      const backendResponse = await fetch('/api/auth/google/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          idToken: response.credential,
        }),
      });

      if (!backendResponse.ok) {
        throw new Error('Login failed');
      }

      const data: GoogleLoginResponse = await backendResponse.json();
      
      // Store token and user info
      localStorage.setItem('jwt_token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      setToken(data.token);
      setUser(data.user);
      
      console.log('Login successful:', data.user);
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed. Please try again.');
    }
  };

  const signIn = () => {
    if (!isLoaded || !window.google) {
      console.error('Google Identity Services not loaded');
      return;
    }

    // Initialize Google One Tap
    window.google.accounts.id.initialize({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      callback: handleCredentialResponse,
    });

    // Trigger the popup
    window.google.accounts.id.prompt((notification: any) => {
      if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
        // Fallback to button if popup is blocked
        window.google.accounts.id.renderButton(
          document.getElementById('buttonDiv'),
          {
            type: 'standard',
            theme: 'outline',
            size: 'large',
          }
        );
      }
    });
  };

  const signOut = () => {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  const getAuthHeaders = () => {
    if (!token) return {};
    
    return {
      'Authorization': `Bearer ${token}`,
    };
  };

  return {
    isLoaded,
    user,
    token,
    signIn,
    signOut,
    getAuthHeaders,
    isAuthenticated: !!token && !!user,
  };
}

export function GoogleSignInButton() {
  const { signIn, isLoaded } = useGoogleAuth();

  if (!isLoaded) {
    return <div>Loading Google Sign-In...</div>;
  }

  return (
    <div>
      <button
        onClick={signIn}
        className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md transition-colors duration-200"
      >
        Sign in with Google
      </button>
      <div id="buttonDiv"></div>
    </div>
  );
}

