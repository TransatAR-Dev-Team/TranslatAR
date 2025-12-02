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
    render(<App />);
    expect(screen.getByText(/TranslatAR Web Portal/i)).toBeInTheDocument();

    // Navigate to the history panel
    fireEvent.click(screen.getByRole("button", { name: /^navigation$/i }));
    const conversationsButton = await screen.findByRole("button", {
      name: /conversations \/ history/i,
    });
    fireEvent.click(conversationsButton);

    // For a logged-out user, it should show the empty state
    expect(
      await screen.findByText(/no saved conversations/i),
    ).toBeInTheDocument();
  });

  it("should display the translation history after a successful fetch", async () => {
    // Mock localStorage to have a token
    const mockToken = "fake-jwt-token";
    localStorage.setItem("translatar_jwt", mockToken);

    // Mock the /api/me call
    fetchMock.mockResponseOnce(
      JSON.stringify({
        email: "test@example.com",
        id: "user123",
        name: "Test User",
      }),
    );

    // Mock the /api/settings call
    fetchMock.mockResponseOnce(
      JSON.stringify({
        settings: {},
      }),
    );

    // Mock the /api/history call (needs to be mocked twice)
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
    // Mock for the first call in initialize()
    fetchMock.mockResponseOnce(JSON.stringify({ history: mockHistory }));
    // Mock for the second call in the useEffect that watches appUser
    fetchMock.mockResponseOnce(JSON.stringify({ history: mockHistory }));

    render(<App />);

    // Navigate to the history panel
    fireEvent.click(screen.getByRole("button", { name: /^navigation$/i }));
    const conversationsButton = await screen.findByRole("button", {
      name: /conversations \/ history/i,
    });
    fireEvent.click(conversationsButton);

    // Wait for the component to finish loading and check for the session list
    await waitFor(() => {
      expect(screen.queryByText(/Loading.../i)).not.toBeInTheDocument();
    });

    // Check that session card is displayed (shows translation count)
    expect(screen.getByText(/2 translations/i)).toBeInTheDocument();

    // Click on the session to view details
    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);

    // Now the translation details should be visible
    expect(screen.getByText(/Hello/i)).toBeInTheDocument();
    expect(screen.getByText(/Adiós/i)).toBeInTheDocument();
  });

  it("should display an error message if the fetch fails", async () => {
    // Mock localStorage to have a token
    const mockToken = "fake-jwt-token";
    localStorage.setItem("translatar_jwt", mockToken);

    // Mock the /api/me call to succeed
    fetchMock.mockResponseOnce(
      JSON.stringify({
        email: "test@example.com",
        id: "user123",
      }),
    );

    // Mock the /api/settings call to succeed
    fetchMock.mockResponseOnce(
      JSON.stringify({
        settings: {},
      }),
    );

    // Mock the /api/history call to fail
    fetchMock.mockReject(new Error("API is unavailable"));

    render(<App />);

    // Navigate to the history panel
    fireEvent.click(screen.getByRole("button", { name: /^navigation$/i }));
    const conversationsButton = await screen.findByRole("button", {
      name: /conversations \/ history/i,
    });
    fireEvent.click(conversationsButton);

    // Wait for the error message to appear in the UI
    const errorMessage = await screen.findByText(
      /Failed to load translation history./i,
    );
    expect(errorMessage).toBeInTheDocument();
    expect(screen.queryByText(/Loading.../i)).not.toBeInTheDocument();
  });
});
