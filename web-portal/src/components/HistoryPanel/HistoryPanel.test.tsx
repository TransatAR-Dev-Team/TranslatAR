import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import HistoryPanel from "./HistoryPanel";

// Use the global fetch mock defined in test-setup.ts
declare let fetchMock: any;

describe("HistoryPanel Component", () => {
  const mockHistory = [
    {
      _id: "1",
      original_text: "Hello",
      translated_text: "Hola",
      source_lang: "en",
      target_lang: "es",
      conversationId: "conv-1",
      timestamp: "2025-11-30T00:00:00Z",
    },
    {
      _id: "2",
      original_text: "Goodbye",
      translated_text: "Adiós",
      source_lang: "en",
      target_lang: "es",
      conversationId: "conv-1",
      timestamp: "2025-11-30T00:01:00Z",
    },
  ];

  beforeEach(() => {
    fetchMock.resetMocks();
    localStorage.clear();
    // Mock the alert function to prevent popups from blocking tests
    vi.spyOn(window, "alert").mockImplementation(() => {});
  });

  // This is a helper function to set up our robust mock
  const setupFetchMocks = (summaryResponse: any, saveResponse: any = {}) => {
    fetchMock.mockImplementation((url: string) => {
      if (url.includes("/api/summarize/history")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ history: [] }),
        });
      }
      if (url.includes("/api/summarize/save")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(saveResponse),
        });
      }
      if (url.includes("/api/summarize")) {
        if (summaryResponse[1]?.status === 500) {
          return Promise.resolve({
            ok: false,
            status: 500,
            json: () => Promise.resolve({ detail: "Server error" }),
          });
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(summaryResponse),
        });
      }
      return Promise.reject(new Error(`Unhandled API call: ${url}`));
    });
  };

  it("shows the loading message when isLoading is true", () => {
    render(<HistoryPanel history={[]} isLoading={true} error={null} />);
    expect(screen.getByText(/loading.../i)).toBeInTheDocument();
  });

  it("shows the error message when an error is provided", () => {
    render(
      <HistoryPanel history={[]} isLoading={false} error="Failed to load." />,
    );
    expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
  });

  it('shows "no saved conversations" when history is empty', () => {
    render(<HistoryPanel history={[]} isLoading={false} error={null} />);
    expect(screen.getByText(/no saved conversations/i)).toBeInTheDocument();
  });

  it("renders the session list correctly", () => {
    render(
      <HistoryPanel history={mockHistory} isLoading={false} error={null} />,
    );
    expect(screen.getByText(/2 translations/i)).toBeInTheDocument();
    expect(screen.getByText(/English → Spanish/i)).toBeInTheDocument();
  });

  it("shows translation details when a session is clicked", async () => {
    setupFetchMocks({}); // Mock the history fetch
    render(
      <HistoryPanel history={mockHistory} isLoading={false} error={null} />,
    );
    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);
    await waitFor(() => {
      expect(screen.getByText("Hello")).toBeInTheDocument();
      expect(screen.getByText("Adiós")).toBeInTheDocument();
    });
  });

  it("shows summarize button when conversation is selected", async () => {
    setupFetchMocks({});
    render(
      <HistoryPanel history={mockHistory} isLoading={false} error={null} />,
    );
    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);
    expect(
      await screen.findByRole("button", { name: /summarize/i }),
    ).toBeInTheDocument();
  });

  it("calls API and displays summary when summarize is clicked", async () => {
    setupFetchMocks({ summary: "This is a test summary." });
    render(
      <HistoryPanel history={mockHistory} isLoading={false} error={null} />,
    );

    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);

    const summarizeButton = await screen.findByRole("button", {
      name: /summarize/i,
    });
    fireEvent.click(summarizeButton);

    expect(
      await screen.findByText(/This is a test summary./i),
    ).toBeInTheDocument();
  });

  it("shows save button when summary is displayed", async () => {
    setupFetchMocks({ summary: "Test summary" });
    render(
      <HistoryPanel history={mockHistory} isLoading={false} error={null} />,
    );

    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);

    const summarizeButton = await screen.findByRole("button", {
      name: /summarize/i,
    });
    fireEvent.click(summarizeButton);

    await screen.findByText(/Test summary/i);

    const saveButton = screen.getByRole("button", { name: /^Save$/i });
    expect(saveButton).toBeInTheDocument();
  });

  it("calls save API when save button is clicked", async () => {
    setupFetchMocks({ summary: "Test summary" });
    localStorage.setItem("translatar_jwt", "fake-token");

    render(
      <HistoryPanel history={mockHistory} isLoading={false} error={null} />,
    );

    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);

    const summarizeButton = await screen.findByRole("button", {
      name: /summarize/i,
    });
    fireEvent.click(summarizeButton);

    await screen.findByText(/Test summary/i);
    const saveButton = screen.getByRole("button", { name: /^Save$/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/summarize/save",
        expect.any(Object),
      );
    });
  });

  it("displays error message when summarization fails", async () => {
    // Mock a 500 error for the summarize endpoint
    setupFetchMocks(["Error", { status: 500 }]);
    render(
      <HistoryPanel history={mockHistory} isLoading={false} error={null} />,
    );

    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);

    const summarizeButton = await screen.findByRole("button", {
      name: /summarize/i,
    });
    fireEvent.click(summarizeButton);

    expect(
      await screen.findByText(/failed to generate summary/i),
    ).toBeInTheDocument();
  });
});
