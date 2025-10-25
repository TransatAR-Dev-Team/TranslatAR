import React from 'react';
import { useAuth } from './AuthContext';
import GoogleButton from 'react-google-button';

interface GoogleLoginButtonProps {
  className?: string;
}

const GoogleLoginButton: React.FC<GoogleLoginButtonProps> = ({ className = '' }) => {
  const { user, login, logout } = useAuth();

  if (user) {
    return (
      <div className={`flex items-center space-x-3 bg-white rounded-lg px-4 py-3 shadow-sm border border-gray-200 ${className}`}>
        {user.picture && (
          <img
            src={user.picture}
            alt={user.name}
            className="w-8 h-8 rounded-full flex-shrink-0"
          />
        )}
        <div className="flex flex-col min-w-0">
          <span className="text-sm font-medium text-gray-900 truncate">{user.name}</span>
          <span className="text-xs text-gray-500 truncate">{user.email}</span>
        </div>
        <button
          onClick={logout}
          className="bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 hover:shadow-sm flex-shrink-0"
        >
          Logout
        </button>
      </div>
    );
  }

  return (
    <div className={className}>
      <GoogleButton
        onClick={login}
        label="Sign in with Google"
        style={{
          width: '100%',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        }}
      />
    </div>
  );
};

export default GoogleLoginButton;