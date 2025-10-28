import { CredentialResponse, GoogleLogin } from '@react-oauth/google';
import { jwtDecode, JwtPayload } from 'jwt-decode';

interface GoogleIdTokenPayload extends JwtPayload {
  email?: string;
  email_verified?: boolean;
  name?: string;
  picture?: string;
  given_name?: string;
  family_name?: string;
}

interface GoogleLoginButtonProps {
  onLoginSuccess: (decodedToken: GoogleIdTokenPayload, credentialResponse: CredentialResponse) => void;
  onLoginError: () => void;
}

export default function GoogleLoginButton({ onLoginSuccess, onLoginError }: GoogleLoginButtonProps) {

  const handleSuccess = (credentialResponse: CredentialResponse) => {
    console.log("Google login success. Credential response: ", credentialResponse);
    const idToken = credentialResponse.credential;

    if (!idToken) {
        console.error("login successful but no id token found");
        alert("login succeeded but failed to get user details");
        onLoginError();
        return;
    }

    console.log("ID token JWT: ", idToken);
    try {
      const decodedToken = jwtDecode<GoogleIdTokenPayload>(idToken);
      console.log("decoded token:", decodedToken);
      onLoginSuccess(decodedToken, credentialResponse);
    } catch (error) {
      console.error("error decoding JWT token:", error);
      alert("Failed to process login info");
      onLoginError();
    }
  };

  const handleError = () => {
    console.error('Google Login Failed');
    alert('Login Failed. Check the console for details.');
    onLoginError();
  };

  return (
    <GoogleLogin
      onSuccess={handleSuccess}
      onError={handleError}
    />
  );
}
