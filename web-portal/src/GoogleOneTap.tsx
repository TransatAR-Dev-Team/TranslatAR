import React, { useEffect, useRef } from 'react';
import { useAuth } from './AuthContext';

interface GoogleOneTapProps {
  className?: string;
}

declare global {
  interface Window {
    google?: {
      accounts?: {
        id: {
          initialize: (config: any) => void;
          prompt: (callback?: (notification: any) => void) => void;
          disableAutoSelect: () => void;
        };
      };
    };
  }
}

const GoogleOneTap: React.FC<GoogleOneTapProps> = ({ className = '' }) => {
  const { user, isLoading, handleOneTapSuccess } = useAuth();
  const oneTapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (user || isLoading) return;

    if (window.google?.accounts?.id) {
      window.google.accounts.id.disableAutoSelect();
    }

    const initializeOneTap = () => {
      if (!window.google?.accounts?.id) {
        setTimeout(initializeOneTap, 100);
        return;
      }

      window.google.accounts.id.initialize({
        client_id: 'YOUR_GOOGLE_CLIENT_ID', // Placeholder for security
        callback: handleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: false,
        context: 'signup',
        itp_support: true,
        use_fedcm_for_prompt: true,
        ux_mode: 'popup',
        login_uri: window.location.origin
      });

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
        const backendResponse = await fetch('http://localhost:8000/auth/google/one-tap', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ credential: response.credential }),
        });

        if (backendResponse.ok) {
          const data = await backendResponse.json();
          await handleOneTapSuccess(data.jwt, data.user);
          console.log('One-tap authentication successful');
        } else {
          console.error('One-tap authentication failed');
        }
      } catch (error) {
        console.error('One-tap error:', error);
      }
    };

    setTimeout(initializeOneTap, 500);
  }, [user, isLoading, handleOneTapSuccess]);

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

export default GoogleOneTap;
