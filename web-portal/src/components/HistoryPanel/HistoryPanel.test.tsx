import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import HistoryPanel from "./HistoryPanel";

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
});
