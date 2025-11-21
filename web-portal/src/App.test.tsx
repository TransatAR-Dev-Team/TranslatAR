import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import App from "./App";

declare let fetchMock: typeof vi & {
  mockResponseOnce: (body: string, init?: ResponseInit) => void;
};

describe("App Component", () => {
  beforeEach(() => {
    fetchMock.resetMocks();
    localStorage.clear(); // Clean up localStorage between tests
  });

  it("should render the main heading and show the initial history state", async () => {
    fetchMock.mockResponseOnce(JSON.stringify({ settings: {} })); // For initial loadSettings
    fetchMock.mockResponseOnce(JSON.stringify({})); // For initial loadLogs

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
    const mockToken = "fake-jwt-token";
    localStorage.setItem("translatar_jwt", mockToken);

    // --- MOCKS FOR THE INITIAL `initialize` CALL ---
    fetchMock.mockResponseOnce(JSON.stringify({ email: "test@example.com" })); // 1. /api/me
    fetchMock.mockResponseOnce(JSON.stringify({ settings: {} })); // 2. /api/settings
    const mockHistory = {
      history: [
        {
          _id: "1",
          original_text: "Hello",
          translated_text: "Hola",
          source_lang: "en",
          target_lang: "es",
        },
        {
          _id: "2",
          original_text: "Goodbye",
          translated_text: "Adiós",
          source_lang: "en",
          target_lang: "es",
        },
      ],
    };
    fetchMock.mockResponseOnce(JSON.stringify(mockHistory)); // 3. /api/history (first time)
    fetchMock.mockResponseOnce(JSON.stringify([])); // 4. /api/transcripts (for loadLogs)

    // --- MOCKS FOR THE SECOND `useEffect` CALL (after appUser is set) ---
    fetchMock.mockResponseOnce(JSON.stringify(mockHistory)); // 5. /api/history (second time)
    fetchMock.mockResponseOnce(JSON.stringify([])); // 6. /api/transcripts (second time)
    fetchMock.mockResponseOnce(JSON.stringify({ settings: {} })); // 7. /api/settings (second time)

    render(<App />);

    // Navigate to the history panel
    fireEvent.click(screen.getByRole("button", { name: /^navigation$/i }));
    const conversationsButton = await screen.findByRole("button", {
      name: /conversations \/ history/i,
    });
    fireEvent.click(conversationsButton);

    // Wait for the component to finish loading and check for the data
    await waitFor(() => {
      expect(screen.queryByText(/Loading history.../i)).not.toBeInTheDocument();
    });

    expect(screen.getByText(/Hello/i)).toBeInTheDocument();
    expect(screen.getByText(/Adiós/i)).toBeInTheDocument();
  });

  it("should display an error message if the fetch fails", async () => {
    // Mock localStorage to have a token
    const mockToken = "fake-jwt-token";
    localStorage.setItem("translatar_jwt", mockToken);

    // Mock initial calls, but make the first history call fail
    fetchMock.mockResponseOnce(JSON.stringify({ email: "test@example.com" })); // /api/me
    fetchMock.mockResponseOnce(JSON.stringify({ settings: {} })); // /api/settings
    fetchMock.mockRejectOnce(new Error("API is unavailable")); // /api/history -> FAILS
    fetchMock.mockResponseOnce(JSON.stringify([])); // /api/transcripts

    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: /^navigation$/i }));
    const conversationsButton = await screen.findByRole("button", {
      name: /conversations \/ history/i,
    });
    fireEvent.click(conversationsButton);

    const errorMessage = await screen.findByText(
      /Failed to load translation history./i,
    );
    expect(errorMessage).toBeInTheDocument();
  });
});
