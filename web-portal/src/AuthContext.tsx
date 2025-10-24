import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: () => void;
  logout: () => void;
  verifyToken: (token: string) => Promise<boolean>;
  handleOneTapSuccess: (jwt: string, userData: any) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token');
    if (savedToken) {
      verifyToken(savedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const verifyToken = async (tokenToVerify: string): Promise<boolean> => {
    try {
      const response = await fetch(`http://localhost:8000/auth/verify?token=${tokenToVerify}`);
      if (response.ok) {
        const data = await response.json();
        setToken(tokenToVerify);
        setUser(data.user);
        setIsLoading(false);
        return true;
      } else {
        localStorage.removeItem('auth_token');
        setToken(null);
        setUser(null);
        setIsLoading(false);
        return false;
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      localStorage.removeItem('auth_token');
      setToken(null);
      setUser(null);
      setIsLoading(false);
      return false;
    }
  };

  const login = () => {
    window.location.href = 'http://localhost:8000/auth/google';
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
  };

  const handleOneTapSuccess = async (jwt: string, userData: any) => {
    setToken(jwt);
    setUser(userData);
    localStorage.setItem('auth_token', jwt);
    setIsLoading(false);
  };

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    login,
    logout,
    verifyToken,
    handleOneTapSuccess,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
