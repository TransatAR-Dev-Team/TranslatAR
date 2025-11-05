import type { CredentialResponse } from "@react-oauth/google";
import type { User } from "../models/User";
import GoogleLoginButton from "./GoogleLoginButton/GoogleLoginButton";

interface HeaderProps {
  appUser: User | null;
  onLoginSuccess: (credentialResponse: CredentialResponse) => void;
  onLoginError: () => void;
  onLogout: () => void;
  onShowSettings: () => void;
}

export default function Header({
  appUser,
  onLoginSuccess,
  onLoginError,
  onLogout,
  onShowSettings,
}: HeaderProps) {
  return (
    <div className="flex justify-between items-center mb-8">
      <h1 className="text-4xl font-bold">TranslatAR Web Portal</h1>
      <div className="flex items-center space-x-4">
        {appUser ? (
          <>
            <span className="text-gray-300">Welcome, {appUser.email}</span>
            <button
              onClick={onLogout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors duration-200"
            >
              Logout
            </button>
          </>
        ) : (
          <GoogleLoginButton
            onLoginSuccess={onLoginSuccess}
            onLoginError={onLoginError}
          />
        )}
        <button
          onClick={onShowSettings}
          className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-md transition-colors duration-200"
        >
          Settings
        </button>
      </div>
    </div>
  );
}
