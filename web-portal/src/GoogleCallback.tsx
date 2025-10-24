import React, { useEffect } from 'react';
import { useAuth } from './AuthContext';

const GoogleCallback: React.FC = () => {
  const { login } = useAuth();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
      login(token);
      // Redirect to main app
      window.location.href = '/';
    }
  }, [login]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
        <p className="mt-4 text-lg text-gray-600">Completing sign-in...</p>
      </div>
    </div>
  );
};

export default GoogleCallback;
