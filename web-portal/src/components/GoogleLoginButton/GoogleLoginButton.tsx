import type { CredentialResponse } from "@react-oauth/google";
import { GoogleLogin } from "@react-oauth/google";

interface GoogleLoginButtonProps {
  onLoginSuccess: (credentialResponse: CredentialResponse) => void;
  onLoginError: () => void;
}

export default function GoogleLoginButton({
  onLoginSuccess,
  onLoginError,
}: GoogleLoginButtonProps) {
  const handleSuccess = (credentialResponse: CredentialResponse) => {
    console.log("Google login success. Passing credential response to parent.");
    onLoginSuccess(credentialResponse);
  };

  const handleError = () => {
    console.error("Google Login Failed");
    alert("Login Failed. Check the console for details.");
    onLoginError();
  };

  return <GoogleLogin onSuccess={handleSuccess} onError={handleError} />;
}
