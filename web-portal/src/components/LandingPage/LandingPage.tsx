import type { CredentialResponse } from "@react-oauth/google";
import GoogleLoginButton from "../GoogleLoginButton/GoogleLoginButton";
import melvinLogo from "../../../public/melvinLogo.png";

interface LandingPageProps {
  onLoginSuccess: (credentialResponse: CredentialResponse) => void;
  onLoginError: () => void;
}

export default function LandingPage({
  onLoginSuccess,
  onLoginError,
}: LandingPageProps) {
  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-4 text-center">
      <div className="max-w-md w-full bg-slate-800 rounded-xl shadow-2xl p-8 border border-slate-700">
        <img
          src={melvinLogo}
          alt="TranslatAR Logo"
          className="mx-auto h-28 w-auto mb-6"
        />

        <h1 className="text-5xl font-bold text-white mb-2">TranslatAR</h1>

        <p className="text-slate-300 mb-8">
          Please sign in to access your dashboard.
        </p>

        <div className="flex justify-center">
          <GoogleLoginButton
            onLoginSuccess={onLoginSuccess}
            onLoginError={onLoginError}
          />
        </div>
      </div>
    </div>
  );
}
