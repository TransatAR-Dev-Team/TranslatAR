import { describe, it, expect, beforeEach, vi } from "vitest";
import { loginWithGoogleApi, getMeApi } from "./auth";

// Enable fetch mocking
declare let fetchMock: any;

describe("Auth API", () => {
  beforeEach(() => {
    fetchMock.resetMocks();
    vi.spyOn(console, "error").mockImplementation(() => {}); // Silence console.errors
    vi.spyOn(console, "log").mockImplementation(() => {});
  });

  describe("loginWithGoogleApi", () => {
    it("throws an error if token is missing", async () => {
      await expect(loginWithGoogleApi("")).rejects.toThrow(
        "Google ID Token is missing.",
      );
    });

    it("returns access token on successful login", async () => {
      const mockResponse = {
        access_token: "app-jwt-123",
        token_type: "bearer",
      };

      fetchMock.mockResponseOnce(JSON.stringify(mockResponse));

      const result = await loginWithGoogleApi("google-id-token");

      expect(result).toEqual(mockResponse);
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/auth/google/login",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ token: "google-id-token" }),
        }),
      );
    });

    it("throws specific error message from backend on failure", async () => {
      fetchMock.mockResponseOnce(
        JSON.stringify({ detail: "Invalid Google Token" }),
        { status: 401 },
      );

      await expect(loginWithGoogleApi("bad-token")).rejects.toThrow(
        "Invalid Google Token",
      );
    });

    it("throws generic error message if backend JSON is empty or missing detail", async () => {
      fetchMock.mockResponseOnce("{}", { status: 500 });

      await expect(loginWithGoogleApi("token")).rejects.toThrow(
        "Backend Google login failed with status 500",
      );
    });

    it("handles network crashes gracefully", async () => {
      fetchMock.mockReject(new Error("Network Error"));

      await expect(loginWithGoogleApi("token")).rejects.toThrow(
        "Network Error",
      );
    });
  });

  describe("getMeApi", () => {
    it("throws error if token is missing", async () => {
      await expect(getMeApi("")).rejects.toThrow(
        "Authentication token is missing.",
      );
    });

    it("returns user profile on success", async () => {
      const mockUser = {
        _id: "u1",
        email: "test@example.com",
        googleId: "g1",
      };
      fetchMock.mockResponseOnce(JSON.stringify(mockUser));

      const result = await getMeApi("valid-jwt");

      expect(result).toEqual(mockUser);
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/users/me",
        expect.objectContaining({
          headers: { Authorization: "Bearer valid-jwt" },
        }),
      );
    });

    it("throws error on 401/403 responses", async () => {
      fetchMock.mockResponseOnce("Unauthorized", { status: 401 });

      await expect(getMeApi("expired-jwt")).rejects.toThrow(
        "Failed to fetch user details",
      );
    });
  });
});
