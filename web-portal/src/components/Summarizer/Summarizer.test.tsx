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

  it("alerts when trying to save without being logged in", async () => {
    vi.spyOn(window, "alert").mockImplementation(() => {});

    render(<Summarizer />);

    const textarea = screen.getByPlaceholderText(/paste or type text here/i);
    fireEvent.change(textarea, { target: { value: "Some text" } });

    fetchMock.mockResponseOnce(
      JSON.stringify({ summary: "Generated summary" }),
    );
    fireEvent.click(screen.getByRole("button", { name: /summarize/i }));

    const saveButton = await screen.findByText(/save/i);
    fireEvent.click(saveButton);

    expect(window.alert).toHaveBeenCalledWith(
      "You must be logged in to save a summary.",
    );
  });

  it("calls API to save summary when logged in", async () => {
    localStorage.setItem("translatar_jwt", "fake-token");

    fetchMock.mockResponseOnce(
      JSON.stringify({ summary: "Generated summary" }),
    ); // For summarization
    fetchMock.mockResponseOnce(JSON.stringify({})); // For save API

    render(<Summarizer />);

    const textarea = screen.getByPlaceholderText(/paste or type text here/i);
    fireEvent.change(textarea, { target: { value: "Some text" } });
    fireEvent.click(screen.getByRole("button", { name: /summarize/i }));

    const saveButton = await screen.findByText(/save/i);

    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
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

  it("fetches and displays advice on success", async () => {
    fetchMock.mockResponseOnce(JSON.stringify({ advice: "Do this!" }));
    render(<Summarizer />);
    fireEvent.change(screen.getByPlaceholderText(/paste or type text here/i), {
      target: { value: "Some text" },
    });
    fireEvent.click(screen.getByText(/give me advice/i));
    expect(await screen.findByText(/Do this!/i)).toBeInTheDocument();
  });

  it("displays error if advice API call fails", async () => {
    fetchMock.mockResponseOnce("Error", { status: 500 });
    render(<Summarizer />);
    fireEvent.change(screen.getByPlaceholderText(/paste or type text here/i), {
      target: { value: "Some text" },
    });
    fireEvent.click(screen.getByText(/give me advice/i));
    expect(
      await screen.findByText(/failed to generate advice/i),
    ).toBeInTheDocument();
  });

  it("displays a notification message when summary length is auto-downgraded", async () => {
    const notificationMessage =
      "Your text was too short for a long summary, so a medium summary was generated instead.";
    fetchMock.mockResponseOnce(
      JSON.stringify({
        summary: "This is the summary.",
        message: notificationMessage,
      }),
    );

    render(<Summarizer />);
    const textarea = screen.getByPlaceholderText(/paste or type text here/i);
    const button = screen.getByRole("button", { name: /summarize/i });

    fireEvent.change(textarea, { target: { value: "A short text." } });
    fireEvent.click(button);

    expect(await screen.findByText(notificationMessage)).toBeInTheDocument();
    expect(await screen.findByText("This is the summary.")).toBeInTheDocument();
  });
});
