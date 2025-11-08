import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import Summarizer from "./Summarizer";

declare let fetchMock: typeof vi & {
  mockResponseOnce: (body: string, init?: ResponseInit) => void;
};

describe("Summarizer Component", () => {
  beforeEach(() => {
    fetchMock.resetMocks();
  });

  it("renders the textarea and allows user input", () => {
    render(<Summarizer />);
    const textarea = screen.getByPlaceholderText(/paste or type text here/i);
    fireEvent.change(textarea, { target: { value: "This is a test." } });
    expect(textarea).toHaveValue("This is a test.");
  });

  it("shows an error if the button is clicked with no text", async () => {
    render(<Summarizer />);
    fireEvent.click(screen.getByRole("button", { name: /summarize/i }));
    expect(
      await screen.findByText(/please enter some text/i),
    ).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("calls the API and displays the summary on success", async () => {
    fetchMock.mockResponseOnce(
      JSON.stringify({ summary: "This is the final summary." }),
    );

    render(<Summarizer />);
    const textarea = screen.getByPlaceholderText(/paste or type text here/i);
    const button = screen.getByRole("button", { name: /summarize/i });

    fireEvent.change(textarea, { target: { value: "A long piece of text." } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/summarizing.../i)).toBeInTheDocument();
      expect(button).toBeDisabled();
    });

    expect(
      await screen.findByText("This is the final summary."),
    ).toBeInTheDocument();

    expect(button).not.toBeDisabled();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/summarize",
      expect.any(Object),
    );
  });

  it("displays an error message if the API call fails", async () => {
    fetchMock.mockResponseOnce("Error", { status: 500 });

    render(<Summarizer />);
    fireEvent.change(screen.getByPlaceholderText(/paste or type text here/i), {
      target: { value: "A long piece of text." },
    });
    fireEvent.click(screen.getByRole("button", { name: /summarize/i }));

    expect(
      await screen.findByText(/failed to generate summary/i),
    ).toBeInTheDocument();
  });
});
