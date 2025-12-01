import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import App from "./App";

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
      timestamp: new Date().toISOString(),
    },
    {
      _id: "2",
      original_text: "Goodbye",
      translated_text: "Adiós",
      source_lang: "en",
      target_lang: "es",
      timestamp: new Date().toISOString(),
    },
  ];

  beforeEach(() => {
    globalThis.fetchMock.resetMocks();
    localStorage.clear();
  });

  it("should render the main heading and show the initial history state", async () => {
    render(<App />);
    expect(screen.getByText(/TranslatAR Web Portal/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /^navigation$/i }));
    const conversationsButton = await screen.findByRole("button", {
      name: /conversations \/ history/i,
    });
    fireEvent.click(conversationsButton);

    expect(
      await screen.findByText(/no translations found in the database/i),
    ).toBeInTheDocument();
  });

  it("should display the translation history after a successful fetch", async () => {
    localStorage.setItem("translatar_jwt", mockToken);

    fetchMock.mockImplementation((url) => {
      const u = url.toString();

      if (u.includes("/api/me")) {
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

    fireEvent.click(screen.getByRole("button", { name: /^navigation$/i }));
    const conversationsButton = await screen.findByRole("button", {
      name: /conversations \/ history/i,
    });
    fireEvent.click(conversationsButton);

    await waitFor(() =>
      expect(screen.queryByText(/Loading history.../i)).not.toBeInTheDocument(),
    );

    expect(screen.getByText(/Hello/i)).toBeInTheDocument();
    expect(screen.getByText(/Adiós/i)).toBeInTheDocument();
  });

  it("displays summary history after successful fetch", async () => {
    localStorage.setItem("translatar_jwt", mockToken);

    fetchMock.mockImplementation((url) => {
      if (url.includes("/api/summarize/history")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              history: [
                { _id: "s1", summary: "Summary 1", original_text: "Text 1" },
                { _id: "s2", summary: "Summary 2", original_text: "Text 2" },
              ],
            }),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: /^navigation$/i }));
    const summaryHistoryButton = await screen.findByRole("button", {
      name: /summary history/i,
    });
    fireEvent.click(summaryHistoryButton);

    expect(await screen.findByText(/Summary 1/i)).toBeInTheDocument();
    expect(await screen.findByText(/Summary 2/i)).toBeInTheDocument();
  });
});
