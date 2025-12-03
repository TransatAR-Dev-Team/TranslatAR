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

  const mockUser = {
    email: "test@example.com",
    id: "user123",
    name: "Test User",
  };

  const mockSettings = { settings: {} };

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

  it("should render the main heading and the dashboard by default", async () => {
    render(<App />);

    // Use getByRole 'heading' to specifically find the title, avoiding paragraph text
    expect(
      screen.getByRole("heading", { name: /TranslatAR Web Portal/i }),
    ).toBeInTheDocument();

    // Check that we default to the Dashboard by looking for its specific header
    expect(
      screen.getByRole("heading", { name: /^Dashboard$/i }),
    ).toBeInTheDocument();

    expect(screen.getByText(/What you can do here/i)).toBeInTheDocument();
  });

  it("should navigate to translation history via sidebar and display data", async () => {
    localStorage.setItem("translatar_jwt", mockToken);

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

    // 1. Open Sidebar using the hamburger button
    const navButton = screen.getByRole("button", {
      name: /open navigation menu/i,
    });
    fireEvent.click(navButton);

    // 2. Click the specific history tab
    const conversationsButton = await screen.findByRole("button", {
      name: /conversations \/ history/i,
    });
    fireEvent.click(conversationsButton);

    // 3. Wait for data to load
    await waitFor(() => {
      expect(screen.queryByText(/Loading.../i)).not.toBeInTheDocument();
    });
    it("displays summary history after successful fetch via sidebar navigation", async () => {
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

      // 1. Open Sidebar
      const navButton = screen.getByRole("button", {
        name: /open navigation menu/i,
      });
      fireEvent.click(navButton);

      // 2. Click Summary History tab
      const summaryHistoryButton = await screen.findByRole("button", {
        name: /summary history/i,
      });
      fireEvent.click(summaryHistoryButton);

      // 3. Verify content
      expect(await screen.findByText(/Summary 1/i)).toBeInTheDocument();
      expect(await screen.findByText(/Summary 2/i)).toBeInTheDocument();
    });
    // 4. Verify content matches mockHistory
    expect(screen.getByText(/2 translations/i)).toBeInTheDocument();

    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);

    expect(screen.getByText(/Hello/i)).toBeInTheDocument();
    expect(screen.getByText(/Adiós/i)).toBeInTheDocument();
  });
});
