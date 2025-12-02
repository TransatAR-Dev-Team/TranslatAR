import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import HistoryPanel from "./HistoryPanel";

declare let fetchMock: typeof vi & {
  mockReset: () => void;
  mockResponseOnce: (body: string, init?: ResponseInit) => void;
};

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
    // @ts-ignore
    if (globalThis.fetchMock) {
      // @ts-ignore
      globalThis.fetchMock.resetMocks();
    }
    localStorage.clear();
  });

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
    // Check session card shows translation count
    expect(screen.getByText(/2 translations/i)).toBeInTheDocument();
    // Check language display
    expect(screen.getByText(/English → Spanish/i)).toBeInTheDocument();
  });

  it("shows translation details when a session is clicked", () => {
    render(
      <HistoryPanel history={mockHistory} isLoading={false} error={null} />,
    );

    // Click on the session card
    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);

    // Now translations should be visible
    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.getByText("Hola")).toBeInTheDocument();
    expect(screen.getByText("Goodbye")).toBeInTheDocument();
    expect(screen.getByText("Adiós")).toBeInTheDocument();
  });

  it("shows summarize button when conversation is selected", () => {
    render(
      <HistoryPanel history={mockHistory} isLoading={false} error={null} />,
    );

    // Click on the session card
    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);

    // Summarize button should appear
    expect(screen.getByRole("button", { name: /summarize/i })).toBeInTheDocument();
  });

  it("calls API and displays summary when summarize is clicked", async () => {
    // @ts-ignore
    globalThis.fetchMock.mockResponseOnce(
      JSON.stringify({ summary: "This is a test summary." }),
    );

    localStorage.setItem("translatar_jwt", "fake-token");

    render(
      <HistoryPanel history={mockHistory} isLoading={false} error={null} />,
    );

    // Click on the session card
    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);

    // Click summarize button
    const summarizeButton = screen.getByRole("button", { name: /summarize/i });
    fireEvent.click(summarizeButton);

    // Wait for summary to appear
    expect(await screen.findByText(/This is a test summary./i)).toBeInTheDocument();
    expect(screen.getByText(/Summary:/i)).toBeInTheDocument();

    // @ts-ignore
    expect(globalThis.fetchMock).toHaveBeenCalledWith(
      "/api/summarize",
      expect.objectContaining({
        method: "POST",
        body: expect.stringContaining("Hello Goodbye"),
      }),
    );
  });

  it("shows save button when summary is displayed", async () => {
    // @ts-ignore
    globalThis.fetchMock.mockResponseOnce(
      JSON.stringify({ summary: "Test summary" }),
    );

    render(
      <HistoryPanel history={mockHistory} isLoading={false} error={null} />,
    );

    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);

    const summarizeButton = screen.getByRole("button", { name: /summarize/i });
    fireEvent.click(summarizeButton);

    await waitFor(() => {
      expect(screen.getByText(/Test summary/i)).toBeInTheDocument();
    });

    expect(screen.getByRole("button", { name: /save/i })).toBeInTheDocument();
  });

  it("calls save API when save button is clicked", async () => {
    // @ts-ignore
    globalThis.fetchMock.mockResponseOnce(
      JSON.stringify({ summary: "Test summary" }),
    );
    // @ts-ignore
    globalThis.fetchMock.mockResponseOnce(JSON.stringify({}));

    localStorage.setItem("translatar_jwt", "fake-token");

    const mockOnSummarySaved = vi.fn();

    render(
      <HistoryPanel 
        history={mockHistory} 
        isLoading={false} 
        error={null}
        onSummarySaved={mockOnSummarySaved}
      />,
    );

    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);

    const summarizeButton = screen.getByRole("button", { name: /summarize/i });
    fireEvent.click(summarizeButton);

    await waitFor(() => {
      expect(screen.getByText(/Test summary/i)).toBeInTheDocument();
    });

    const saveButton = screen.getByRole("button", { name: /save/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      // @ts-ignore
      expect(globalThis.fetchMock).toHaveBeenCalledWith(
        "/api/summarize/save",
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            Authorization: "Bearer fake-token",
          }),
        }),
      );
    });
  });

  it("displays error message when summarization fails", async () => {
    // @ts-ignore
    globalThis.fetchMock.mockResponseOnce("Error", { status: 500 });

    render(
      <HistoryPanel history={mockHistory} isLoading={false} error={null} />,
    );

    const sessionCard = screen.getByText(/2 translations/i).closest("div");
    fireEvent.click(sessionCard!);

    const summarizeButton = screen.getByRole("button", { name: /summarize/i });
    fireEvent.click(summarizeButton);

    expect(
      await screen.findByText(/failed to generate summary/i),
    ).toBeInTheDocument();
  });
});