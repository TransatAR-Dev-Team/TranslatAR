import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import DashboardOverview from "./DashboardOverview";
import type { User } from "../../models/User";

describe("DashboardOverview Component", () => {
  const mockUser: User = {
    _id: "123",
    googleId: "g123",
    email: "test@example.com",
  };

  const mockHistoryItem = {
    _id: "h1",
    original_text: "Hello World",
    translated_text: "Hola Mundo",
    timestamp: new Date().toISOString(),
  };

  it("displays the 'Log in' message when no user is provided", () => {
    render(
      <DashboardOverview
        appUser={null}
        history={[]}
        onOpenSummarization={() => {}}
        onOpenHistory={() => {}}
      />,
    );

    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Log in with your Google account to sync/i),
    ).toBeInTheDocument();
    expect(screen.queryByText(/Welcome back/i)).not.toBeInTheDocument();
  });

  it("displays the 'Welcome back' message when a user is logged in", () => {
    render(
      <DashboardOverview
        appUser={mockUser}
        history={[]}
        onOpenSummarization={() => {}}
        onOpenHistory={() => {}}
      />,
    );

    expect(screen.getByText(/Welcome back/i)).toBeInTheDocument();
    expect(
      screen.queryByText(/Log in with your Google account/i),
    ).not.toBeInTheDocument();
  });

  it("displays empty state message when history is empty", () => {
    render(
      <DashboardOverview
        appUser={mockUser}
        history={[]}
        onOpenSummarization={() => {}}
        onOpenHistory={() => {}}
      />,
    );

    expect(
      screen.getByText(/No conversations logged yet/i),
    ).toBeInTheDocument();
    expect(
      screen.queryByText(/Most recent conversation/i),
    ).not.toBeInTheDocument();
  });

  it("displays recent activity snapshot when history is populated", () => {
    render(
      <DashboardOverview
        appUser={mockUser}
        history={[mockHistoryItem]}
        onOpenSummarization={() => {}}
        onOpenHistory={() => {}}
      />,
    );

    // Check count text
    expect(screen.getByText(/You have/i)).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument(); // The count

    // Check the content of the most recent item
    expect(screen.getByText(/Most recent conversation/i)).toBeInTheDocument();
    expect(screen.getByText("Hello World")).toBeInTheDocument();
    expect(screen.getByText(/Hola Mundo/i)).toBeInTheDocument();
  });

  it("calls the correct navigation callbacks when quick action buttons are clicked", () => {
    const handleOpenSummarization = vi.fn();
    const handleOpenHistory = vi.fn();

    render(
      <DashboardOverview
        appUser={mockUser}
        history={[]}
        onOpenSummarization={handleOpenSummarization}
        onOpenHistory={handleOpenHistory}
      />,
    );

    // Test Summarization button
    const sumButton = screen.getByRole("button", {
      name: /Open Summarization/i,
    });
    fireEvent.click(sumButton);
    expect(handleOpenSummarization).toHaveBeenCalledTimes(1);

    // Test History button
    const histButton = screen.getByRole("button", {
      name: /View Translation History/i,
    });
    fireEvent.click(histButton);
    expect(handleOpenHistory).toHaveBeenCalledTimes(1);
  });
});
