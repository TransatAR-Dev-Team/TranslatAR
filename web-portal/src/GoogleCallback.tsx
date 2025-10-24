import React, { useEffect } from 'react';

const GoogleCallback: React.FC = () => {
  useEffect(() => {
    const handleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const error = urlParams.get('error');

      if (error) {
        // Send error to parent window
        window.opener?.postMessage({
          type: 'GOOGLE_AUTH_ERROR',
          error: error,
        }, window.location.origin);
        window.close();
        return;
      }

      if (code) {
        try {
          // Exchange code for token
          const response = await fetch('http://localhost:8000/auth/google/callback', {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          });

          if (response.ok) {
            const data = await response.json();
            
            // Send success to parent window
            window.opener?.postMessage({
              type: 'GOOGLE_AUTH_SUCCESS',
              jwt: data.jwt,
              user: data.user,
            }, window.location.origin);
          } else {
            throw new Error('Failed to exchange code for token');
          }
        } catch (error) {
          console.error('Callback error:', error);
          window.opener?.postMessage({
            type: 'GOOGLE_AUTH_ERROR',
            error: 'Failed to complete authentication',
          }, window.location.origin);
        }
      }

      window.close();
    };

    handleCallback();
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p>Completing authentication...</p>
      </div>
    </div>
  );
};

export default GoogleCallback;
