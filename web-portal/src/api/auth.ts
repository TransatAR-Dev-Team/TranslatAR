import type { User } from "../models/User";

interface LoginResponse {
  access_token: string;
  token_type: string;
}

/**
 * Sends a Google ID Token to the backend to log in and get an application JWT.
 * @param token - The raw ID Token string from Google.
 * @returns A promise that resolves to the application's access token and token type.
 */
export const loginWithGoogleApi = async (
  token: string,
): Promise<LoginResponse> => {
  if (!token) {
    throw new Error("Google ID Token is missing.");
  }

  const targetUrl = `/api/auth/google/login`;
  console.log(`[API] Attempting login POST to: ${targetUrl}`);

  try {
    const response = await fetch(targetUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      // The backend expects a JSON body with a 'token' key
      body: JSON.stringify({ token: token }),
    });

    console.log(`[API] Google login response status: ${response.status}`);
    const responseData = await response.json();

    if (!response.ok) {
      const errorMessage =
        responseData?.detail ||
        `Backend Google login failed with status ${response.status}`;
      console.error(
        `[API] Error during Google login: ${errorMessage}`,
        responseData,
      );
      throw new Error(errorMessage);
    }

    console.log(
      "[API] Google login successful, app token received:",
      responseData,
    );
    return responseData as LoginResponse;
  } catch (error) {
    console.error(`[API] Network or parsing error during Google login:`, error);
    if (error instanceof Error) throw error;
    throw new Error("An unknown error occurred during the login process.");
  }
};

/**
 * Fetches the current user's details from the backend using the application's JWT.
 * @param token - The application's JWT, received from the `loginWithGoogleApi` endpoint.
 * @returns A promise that resolves to the full User object from the backend.
 */
export const getMeApi = async (token: string): Promise<User> => {
  if (!token) throw new Error("Authentication token is missing.");

  const response = await fetch("/api/users/me", {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch user details. Token might be invalid.");
  }
  return response.json();
};
