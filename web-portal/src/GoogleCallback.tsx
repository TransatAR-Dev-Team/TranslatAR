import React, { useEffect } from 'react';
import { useAuth } from './AuthContext';

const GoogleCallback: React.FC = () => {
  const { verifyToken } = useAuth();

  useEffect(() => {
    const handleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');
      
      if (token) {
        const isValid = await verifyToken(token);
        if (isValid) {
          // Redirect to main app
          window.location.href = '/';
        } else {
          console.error('Token verification failed');
          // Redirect to main app with error
          window.location.href = '/?error=auth_failed';
        }
      } else {
        console.error('No token in callback');
        // Redirect to main app with error
        window.location.href = '/?error=no_token';
      }
    };

    handleCallback();
  }, [verifyToken]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Processing Google Sign-In...
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Please wait while we complete your authentication.
          </p>
        </div>
      </div>
    </div>
  );
};

export default GoogleCallback;
