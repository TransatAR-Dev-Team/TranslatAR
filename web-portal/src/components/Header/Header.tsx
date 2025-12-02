import type { CredentialResponse } from "@react-oauth/google";
import type { User } from "../../models/User";
import GoogleLoginButton from "../GoogleLoginButton/GoogleLoginButton";

// adjust path if your logo lives somewhere else
import melvinLogo from "../../melvinLogo.png";

interface HeaderProps {
  appUser: User | null;
  onLoginSuccess: (credentialResponse: CredentialResponse) => void;
  onLoginError: () => void;
  onLogout: () => void;
  onShowSettings: () => void;
  onShowNavigation: () => void;
}

export default function Header({
  appUser,
  onLoginSuccess,
  onLoginError,
  onLogout,
  onShowSettings,
  onShowNavigation,
}: HeaderProps) {
  return (
    <header className="mb-6">
      <div className="flex items-center justify-between gap-4">
        {/* Left: hamburger + logo + name */}
        <div className="flex items-center gap-3">
          {/* Hamburger button on the far left */}
          <button
            type="button"
            onClick={onShowNavigation}
            className="inline-flex flex-col justify-center gap-1 p-2 rounded-md border border-slate-600 bg-slate-800 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Open navigation menu"
          >
            <span className="w-5 h-0.5 bg-slate-100 rounded" />
            <span className="w-5 h-0.5 bg-slate-100 rounded" />
            <span className="w-5 h-0.5 bg-slate-100 rounded" />
          </button>

          <div className="flex items-center gap-2">
            <img
              src={melvinLogo}
              alt="TranslatAR logo"
              className="h-24 w-24 rounded-md object-contain"
            />
            <div>
              <h1 className="text-2xl font-bold leading-tight">
                TranslatAR Web Portal
              </h1>
              <p className="text-xs text-slate-300">
                Manage your translations, summaries, and headset settings.
              </p>
            </div>
          </div>
        </div>

        {/* Right: auth + settings */}
        <div className="flex items-center gap-3">
          {appUser ? (
            <>
              <span className="text-sm text-gray-300">
                Welcome, {appUser.email}
              </span>
              <button
                onClick={onLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded-md text-sm transition-colors duration-200"
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
            className="bg-slate-700 hover:bg-slate-600 text-white px-3 py-1.5 rounded-md text-sm transition-colors duration-200"
          >
            Settings
          </button>
        </div>
      </div>
    </header>
  );
}
