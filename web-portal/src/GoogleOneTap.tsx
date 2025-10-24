import React, { useEffect, useRef } from 'react';
import { useAuth } from './AuthContext';

// Extend the Window interface to include Google One-Tap
declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: any) => void;
          prompt: (callback?: (notification: any) => void) => void;
          renderButton: (element: HTMLElement, config: any) => void;
          disableAutoSelect: () => void;
          storeCredential: (credential: any, callback?: () => void) => void;
        };
      };
    };
  }
}

interface GoogleOneTapProps {
  className?: string;
}

export const GoogleOneTap: React.FC<GoogleOneTapProps> = ({ className = '' }) => {
  const { handleOneTapSuccess, user, isLoading } = useAuth();
  const oneTapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Only show one-tap if user is not already logged in
    if (user || isLoading) return;

    // Clear any previous one-tap state
    if (window.google?.accounts?.id) {
      window.google.accounts.id.disableAutoSelect();
    }

    const initializeOneTap = () => {
      if (!window.google?.accounts?.id) {
        // Retry after a short delay if Google script hasn't loaded yet
        setTimeout(initializeOneTap, 100);
        return;
      }

      window.google.accounts.id.initialize({
        client_id: '861587845879-v6ih92nnkk9h1isaiv7gafaqaguockq8.apps.googleusercontent.com',
        callback: handleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: false,
        context: 'signup',
        itp_support: true,
        use_fedcm_for_prompt: true,
        ux_mode: 'popup',
        login_uri: window.location.origin
      });

      // Show the one-tap prompt
      window.google.accounts.id.prompt((notification: any) => {
        console.log('One-tap notification:', notification);
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          console.log('One-tap not displayed');
        }
      });
    };

    const handleCredentialResponse = async (response: any) => {
      try {
        console.log('One-tap credential response:', response);
        
        // Send the credential to your backend for verification
        const backendResponse = await fetch('http://localhost:8000/auth/google/one-tap', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ credential: response.credential }),
        });

        if (backendResponse.ok) {
          const data = await backendResponse.json();
          
          // Update the auth context
          await handleOneTapSuccess(data.jwt, data.user);
          
          console.log('One-tap authentication successful');
        } else {
          console.error('One-tap authentication failed');
        }
      } catch (error) {
        console.error('One-tap error:', error);
      }
    };

    // Initialize after a short delay to ensure Google script is loaded
    setTimeout(initializeOneTap, 500);
  }, [user, isLoading, handleOneTapSuccess]);

  // Don't render anything if user is already logged in or loading
  if (user || isLoading) {
    return null;
  }

  return (
    <div 
      ref={oneTapRef}
      className={`google-one-tap ${className}`}
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: 1000,
        maxWidth: '400px'
      }}
    />
  );
};
