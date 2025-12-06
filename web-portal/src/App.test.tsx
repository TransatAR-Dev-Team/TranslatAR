import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import App from "./App";

// 1. Mock Google OAuth
vi.mock("@react-oauth/google", () => ({
  GoogleOAuthProvider: ({ children }: any) => <div>{children}</div>,
  GoogleLogin: ({ onSuccess, onError }: any) => (
    <div>
      <button onClick={() => onSuccess({ credential: "mock-google-token" })}>
        Trigger Google Success
      </button>
      <button onClick={() => onSuccess({})}>Trigger Google No Token</button>
      <button onClick={() => onError()}>Trigger Google Error</button>
    </div>
  ),
}));

describe("App Component Integration", () => {
  const mockToken = "fake-app-jwt";
  const mockUser = { _id: "u1", email: "test@example.com", googleId: "g1" };
  const mockSettings = { settings: { source_language: "fr" } };
  const mockHistory = { history: [] };

  beforeEach(() => {
    vi.resetAllMocks();
    // @ts-ignore
    fetchMock.resetMocks();
    localStorage.clear();
    vi.spyOn(window, "alert").mockImplementation(() => {});
    vi.spyOn(console, "error").mockImplementation(() => {});
  });

  // --- Helpers ---
  const mockSuccessfulLogin = () => {
    // @ts-ignore
    fetchMock.mockImplementation(async (url: string) => {
      if (url.includes("/api/auth/google/login"))
        return { ok: true, json: async () => ({ access_token: mockToken }) };
      if (url.includes("/api/users/me"))
        return { ok: true, json: async () => mockUser };
      if (url.includes("/api/settings"))
        return { ok: true, json: async () => mockSettings };
      if (url.includes("/api/history"))
        return { ok: true, json: async () => mockHistory };
      return { ok: true, json: async () => ({}) };
    });
  };

  it("renders Landing Page when not logged in", async () => {
    render(<App />);
    expect(
      await screen.findByText("Please sign in to access your dashboard."),
    ).toBeInTheDocument();
  });

  it("handles full successful login flow", async () => {
    mockSuccessfulLogin();
    render(<App />);

    const loginBtn = await screen.findByText("Trigger Google Success");
    fireEvent.click(loginBtn);

    expect(
      await screen.findByText(/welcome, test@example.com/i),
    ).toBeInTheDocument();
    expect(localStorage.getItem("translatar_jwt")).toBe(mockToken);
  });

  it("handles login failure from Google (No Token)", async () => {
    render(<App />);
    const failBtn = await screen.findByText("Trigger Google No Token");
    fireEvent.click(failBtn);

    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith(
        "Missing required token from Google!",
      );
    });
  });

  it("handles login failure from Backend", async () => {
    // @ts-ignore
    fetchMock.mockResponseOnce(JSON.stringify({ detail: "Bad Token" }), {
      status: 401,
    });

    render(<App />);
    const loginBtn = await screen.findByText("Trigger Google Success");
    fireEvent.click(loginBtn);

    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith(
        "Login failed. Please try again.",
      );
    });
  });

  it("handles logout", async () => {
    localStorage.setItem("translatar_jwt", mockToken);
    mockSuccessfulLogin(); // Pre-load success mocks for init

    render(<App />);

    // Wait for dashboard
    await screen.findByText(/welcome, test@example.com/i);

    const logoutBtn = screen.getByRole("button", { name: /logout/i });
    fireEvent.click(logoutBtn);

    expect(
      await screen.findByText("Please sign in to access your dashboard."),
    ).toBeInTheDocument();
    expect(localStorage.getItem("translatar_jwt")).toBeNull();
  });

  it("handles Settings loading and saving", async () => {
    localStorage.setItem("translatar_jwt", mockToken);
    mockSuccessfulLogin();
    render(<App />);

    await screen.findByText(/welcome, test@example.com/i);

    // Open settings
    fireEvent.click(screen.getByRole("button", { name: /^settings$/i }));

    // Override mock for the SAVE operation specifically
    // @ts-ignore
    fetchMock.mockImplementation(async (url, init) => {
      if (url.includes("/api/settings") && init?.method === "POST")
        return { ok: true, json: async () => ({}) };
      // Default fallbacks for re-fetches
      if (url.includes("/api/users/me"))
        return { ok: true, json: async () => mockUser };
      if (url.includes("/api/settings"))
        return { ok: true, json: async () => mockSettings };
      return { ok: true, json: async () => ({}) };
    });

    const saveBtn = await screen.findByRole("button", {
      name: /save settings/i,
    });
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(
        screen.queryByRole("heading", { name: "Settings" }),
      ).not.toBeInTheDocument();
    });
  });

  it("handles History load failure gracefully", async () => {
    localStorage.setItem("translatar_jwt", mockToken);

    // Fail history specifically
    // @ts-ignore
    fetchMock.mockImplementation(async (url: string) => {
      if (url.includes("/api/history")) return { ok: false, status: 500 };
      if (url.includes("/api/users/me"))
        return { ok: true, json: async () => mockUser };
      if (url.includes("/api/settings"))
        return { ok: true, json: async () => mockSettings };
      return { ok: true, json: async () => ({}) };
    });

    render(<App />);
    await screen.findByText(/welcome, test@example.com/i);

    const navBtn = screen.getByLabelText("Open navigation menu");
    fireEvent.click(navBtn);
    const historyBtn = screen.getByText("Conversations / History");
    fireEvent.click(historyBtn);

    expect(
      await screen.findByText("Failed to load translation history."),
    ).toBeInTheDocument();
  });

  it("handles session expiration (fetch profile fails)", async () => {
    localStorage.setItem("translatar_jwt", "expired-token");
    // @ts-ignore
    fetchMock.mockResponseOnce("Unauthorized", { status: 401 });

    render(<App />);

    expect(
      await screen.findByText("Please sign in to access your dashboard."),
    ).toBeInTheDocument();
    expect(localStorage.getItem("translatar_jwt")).toBeNull();
  });
});
