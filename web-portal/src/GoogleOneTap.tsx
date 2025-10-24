import React, { useEffect } from 'react';
import { useAuth } from './AuthContext';

declare global {
  interface Window {
    google: any;
  }
}

const GoogleOneTap: React.FC = () => {
  const { handleOneTapSuccess } = useAuth();

  useEffect(() => {
    const initializeGoogleOneTap = () => {
      if (window.google && window.google.accounts) {
        window.google.accounts.id.initialize({
          client_id: 'YOUR_GOOGLE_CLIENT_ID',
          callback: handleCredentialResponse,
          itp_support: true,
          use_fedcm_for_prompt: true,
          ux_mode: 'popup',
          login_uri: window.location.origin
        });

        // Prompt the One Tap
        window.google.accounts.id.prompt((notification: any) => {
          if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
            // One Tap was not displayed or was skipped
            console.log('Google One Tap was not displayed or was skipped');
          }
        });
      }
    };

    const handleCredentialResponse = async (response: any) => {
      try {
        await handleOneTapSuccess(response.credential);
      } catch (error) {
        console.error('One-tap authentication failed:', error);
      }
    };

    // Initialize when Google script is loaded
    if (window.google && window.google.accounts) {
      initializeGoogleOneTap();
    } else {
      // Wait for Google script to load
      const checkGoogle = setInterval(() => {
        if (window.google && window.google.accounts) {
          clearInterval(checkGoogle);
          initializeGoogleOneTap();
        }
      }, 100);

      // Cleanup interval after 10 seconds
      setTimeout(() => clearInterval(checkGoogle), 10000);
    }
  }, [handleOneTapSuccess]);

  return null; // This component doesn't render anything visible
};

export default GoogleOneTap;
