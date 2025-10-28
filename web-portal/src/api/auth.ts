interface GoogleLoginPayload {
    googleId: string;
    email: string;
}

interface User {
    _id: string;
    googleId: string;
    email: string;
    username?: string;
    profilePicPath?: string;
}

/**
 * Sends Google login details to the backend to find or create a user.
 * @param payload - The login details containing googleId and email.
 * @returns A promise that resolves to the User object from the backend.
 */
export const loginWithGoogleApi = async (payload: GoogleLoginPayload): Promise<User> => {
    if (!payload.googleId || !payload.email) throw new Error("Missing googleId or email in login payload.");

    const targetUrl = `/api/auth/google/login`;
    console.log(`[API] Attempting Google login POST to: ${targetUrl}`);

    try {
        const response = await fetch(targetUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json", "Accept": "application/json" },
            body: JSON.stringify(payload),
        });
        console.log(`[API] Google login response status: ${response.status}`);

        const responseData = await response.json();

        if (!response.ok) {
            const errorMessage = responseData?.error || `Backend Google login failed with status ${response.status}`;
            console.error(`[API] Error during Google login: ${errorMessage}`, responseData);
            throw new Error(errorMessage);
        }

        console.log("[API] Google login successful, user data received:", responseData);
        return responseData as User; // Assume response matches User structure

    } catch (error) {
        console.error(`[API] Network or parsing error during Google login:`, error);
        if (error instanceof Error) throw error;
        throw new Error("An unknown error occurred during the login process.");
    }
};
