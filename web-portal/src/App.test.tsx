import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import App from "./App";

// Mock the global fetch
declare let fetchMock: typeof vi & {
  mockReset: () => void;
  mockImplementation: (
    fn: (url: string | Request) => Promise<Response>,
  ) => void;
};

describe("App Component", () => {
  const mockToken = "fake-jwt-token";
  const mockUser = { email: "test@example.com", id: "user123", name: "Test User" };
  const mockSettings = { settings: {} };
  const mockHistory = [
    { _id: "1", original_text: "Hello", translated_text: "Hola", source_lang: "en", target_lang: "es", conversationId: "conv-1", timestamp: new Date().toISOString() },
    { _id: "2", original_text: "Goodbye", translated_text: "Adiós", source_lang: "en", target_lang: "es", conversationId: "conv-1", timestamp: new Date().toISOString() },
  ];

  beforeEach(() => {
    // @ts-ignore - fetchMock is global in setup
    globalThis.fetchMock.resetMocks();
    localStorage.clear();
  });

  it("should render the Landing Page when not logged in", async () => {
    // 1. Render without a token in localStorage
    render(<App />);

    // 2. Assert that the landing page text is visible
    expect(
      await screen.findByText("Please sign in to access your dashboard."),
    ).toBeInTheDocument();

    // 3. Assert that the main app's navigation button is NOT visible
    expect(
      screen.queryByRole("button", { name: /open navigation menu/i }),
    ).not.toBeInTheDocument();
  });

  it("should render the dashboard by default when logged in", async () => {
    localStorage.setItem("translatar_jwt", mockToken);
    globalThis.fetchMock.mockImplementation((url) => {
      if (url.toString().includes("/api/users/me")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockUser) });
      }
      if (url.toString().includes("/api/settings")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockSettings) });
      }
      if (url.toString().includes("/api/history")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ history: [] }) });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    render(<App />);

    expect(await screen.findByRole("heading", { name: /TranslatAR Web Portal/i })).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: /^Dashboard$/i })).toBeInTheDocument();
  });

  it("should navigate to translation history and display data when logged in", async () => {
    localStorage.setItem("translatar_jwt", mockToken);

    // @ts-ignore
    globalThis.fetchMock.mockImplementation((url) => {
      const u = url.toString();
      if (u.includes("/api/users/me")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockUser) });
      }
      if (u.includes("/api/settings")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockSettings) });
      }
      if (u.includes("/api/history")) {
        // Use the mockHistory with data for this test
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ history: mockHistory }) });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    render(<App />);

    const navButton = await screen.findByRole("button", { name: /open navigation menu/i });
    fireEvent.click(navButton);
    const conversationsButton = await screen.findByRole("button", { name: /conversations \/ history/i });
    fireEvent.click(conversationsButton);

    await waitFor(() => {
      expect(screen.queryByText(/Loading.../i)).not.toBeInTheDocument();
    });

    expect(screen.getByText(/2 translations/i)).toBeInTheDocument();
    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);

    expect(screen.getByText(/Hello/i)).toBeInTheDocument();
    expect(screen.getByText(/Adiós/i)).toBeInTheDocument();
  });
});
