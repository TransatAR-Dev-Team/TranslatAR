import { render, screen } from "@testing-library/react";
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
    },
    {
      _id: "2",
      original_text: "Goodbye",
      translated_text: "Adiós",
      source_lang: "en",
      target_lang: "es",
    },
  ];

  it("shows the loading message when isLoading is true", () => {
    render(<HistoryPanel history={[]} isLoading={true} error={null} />);
    expect(screen.getByText(/loading history.../i)).toBeInTheDocument();
  });

  it("shows the error message when an error is provided", () => {
    render(
      <HistoryPanel history={[]} isLoading={false} error="Failed to load." />,
    );
    expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
  });

  it('shows "no translations found" when history is empty', () => {
    render(<HistoryPanel history={[]} isLoading={false} error={null} />);
    expect(screen.getByText(/no translations found/i)).toBeInTheDocument();
  });

  it("renders the list of history items correctly", () => {
    render(
      <HistoryPanel history={mockHistory} isLoading={false} error={null} />,
    );
    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.getByText("Hola")).toBeInTheDocument();
    expect(screen.getByText("Goodbye")).toBeInTheDocument();
    expect(screen.getByText("Adiós")).toBeInTheDocument();
  });
});
