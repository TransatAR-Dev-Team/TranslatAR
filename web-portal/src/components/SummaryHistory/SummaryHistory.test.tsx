import { render, screen } from "@testing-library/react";
import { describe, it } from "vitest";
import SummaryHistory from "./SummaryHistory";

describe("SummaryHistory Component", () => {
  it("renders empty state if no history", () => {
    render(<SummaryHistory history={[]} />);
    expect(screen.getByText(/no saved summaries yet/i)).toBeInTheDocument();
  });

  it("renders summary history items", () => {
    const history = [
      { summary: "Test summary 1", timestamp: "2025-12-01T12:00:00Z" },
      { summary: "Test summary 2", timestamp: "2025-12-02T12:00:00Z" },
    ];
    render(<SummaryHistory history={history} />);
    expect(screen.getByText(/Test summary 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Test summary 2/i)).toBeInTheDocument();
  });
});
