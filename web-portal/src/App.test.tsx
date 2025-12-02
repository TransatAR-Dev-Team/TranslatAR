import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import App from "./App";

// Mock the global fetch
declare let fetchMock: typeof vi & {
  mockReset: () => void;
  mockImplementation: (
    fn: (url: string | Request) => Promise<Response>
  ) => void;
};

describe("App Component", () => {
  const mockToken = "fake-jwt-token";

  const mockUser = {
    email: "test@example.com",
    id: "user123",
    name: "Test User",
  };

  const mockSettings = { settings: {} };

  // DATA FROM MAIN: Includes conversationId needed for the new HistoryPanel
  const mockHistory = [
    {
      _id: "1",
      original_text: "Hello",
      translated_text: "Hola",
      source_lang: "en",
      target_lang: "es",
      conversationId: "conv-1",
      timestamp: new Date().toISOString(),
    },
    {
      _id: "2",
      original_text: "Goodbye",
      translated_text: "Adiós",
      source_lang: "en",
      target_lang: "es",
      conversationId: "conv-1",
      timestamp: new Date().toISOString(),
    },
  ];

  beforeEach(() => {
    // @ts-ignore - fetchMock is global in setup
    globalThis.fetchMock.resetMocks();
    localStorage.clear();
  });

  it("should render the main heading and show the initial history state", async () => {
    render(<App />);
    expect(screen.getByText(/TranslatAR Web Portal/i)).toBeInTheDocument();

    // Navigate to the history panel (Logic from MAIN)
    fireEvent.click(screen.getByRole("button", { name: /^navigation$/i }));
    const conversationsButton = await screen.findByRole("button", {
      name: /conversations \/ history/i,
    });
    fireEvent.click(conversationsButton);

    // LOGIC FROM MAIN: Expect the new empty state message
    expect(
      await screen.findByText(/no saved conversations/i)
    ).toBeInTheDocument();
  });

  it("should display the translation history after a successful fetch", async () => {
    localStorage.setItem("translatar_jwt", mockToken);

    // LOGIC FROM REDESIGNSUMMARY: More robust mocking for multiple endpoints
    // @ts-ignore
    globalThis.fetchMock.mockImplementation((url) => {
      const u = url.toString();

      if (u.includes("/api/users/me")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockUser),
        });
      }

      if (u.includes("/api/settings")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockSettings),
        });
      }

      if (u.includes("/api/history")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ history: mockHistory }),
        });
      }

      if (u.includes("/api/summarize/history")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ history: [] }),
        });
      }

      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      });
    });

    render(<App />);

    // Navigate (Logic from MAIN)
    fireEvent.click(screen.getByRole("button", { name: /^navigation$/i }));
    const conversationsButton = await screen.findByRole("button", {
      name: /conversations \/ history/i,
    });
    fireEvent.click(conversationsButton);

    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText(/Loading.../i)).not.toBeInTheDocument();
    });

    // ASSERTIONS FROM MAIN: Check for session card and grouped translations
    expect(screen.getByText(/2 translations/i)).toBeInTheDocument();

    // Click on the session to view details
    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);

    // Now the translation details should be visible
    expect(screen.getByText(/Hello/i)).toBeInTheDocument();
    expect(screen.getByText(/Adiós/i)).toBeInTheDocument();
  });

  // NEW TEST FROM REDESIGNSUMMARY
  it("displays summary history after successful fetch", async () => {
    localStorage.setItem("translatar_jwt", mockToken);

    // @ts-ignore
    globalThis.fetchMock.mockImplementation((url) => {
      const u = url.toString();

      // Basic mocks for initialization
      if (u.includes("/api/users/me"))
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockUser),
        });
      if (u.includes("/api/settings"))
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockSettings),
        });
      if (u.includes("/api/history"))
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ history: [] }),
        });

      // The specific mock we are testing
      if (u.includes("/api/summarize/history")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              history: [
                {
                  _id: "s1",
                  summary: "Summary 1",
                  original_text: "Text 1",
                  timestamp: new Date().toISOString(),
                },
                {
                  _id: "s2",
                  summary: "Summary 2",
                  original_text: "Text 2",
                  timestamp: new Date().toISOString(),
                },
              ],
            }),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    render(<App />);

    // Navigate to Summary History
    fireEvent.click(screen.getByRole("button", { name: /^navigation$/i }));
    const summaryHistoryButton = await screen.findByRole("button", {
      name: /summary history/i,
    });
    fireEvent.click(summaryHistoryButton);

    expect(await screen.findByText(/Summary 1/i)).toBeInTheDocument();
    expect(await screen.findByText(/Summary 2/i)).toBeInTheDocument();
  });
});
