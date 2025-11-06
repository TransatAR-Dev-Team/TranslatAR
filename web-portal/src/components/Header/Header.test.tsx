import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Header from "./Header";
import type { User } from "../../models/User";

// Mock the GoogleLoginButton to simplify the test
vi.mock("../GoogleLoginButton/GoogleLoginButton", () => ({
  default: ({ onLoginSuccess }: { onLoginSuccess: () => void }) => (
    <button onClick={onLoginSuccess}>Mock Sign In</button>
  ),
}));

describe("Header Component", () => {
  const mockUser: User = {
    _id: "123",
    email: "test@example.com",
    googleId: "abc",
  };

  it("renders the login button when no user is provided", () => {
    render(
      <Header
        appUser={null}
        onLoginSuccess={() => {}}
        onLoginError={() => {}}
        onLogout={() => {}}
        onShowSettings={() => {}}
      />,
    );
    expect(
      screen.getByRole("button", { name: /mock sign in/i }),
    ).toBeInTheDocument();
    expect(screen.queryByText(/welcome/i)).not.toBeInTheDocument();
  });

  it("renders the welcome message and logout button when a user is provided", () => {
    render(
      <Header
        appUser={mockUser}
        onLoginSuccess={() => {}}
        onLoginError={() => {}}
        onLogout={() => {}}
        onShowSettings={() => {}}
      />,
    );

    expect(screen.getByText(/welcome, test@example.com/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /logout/i })).toBeInTheDocument();
  });

  it("calls the onLogout function when the logout button is clicked", () => {
    const handleLogout = vi.fn();
    render(
      <Header
        appUser={mockUser}
        onLoginSuccess={() => {}}
        onLoginError={() => {}}
        onLogout={handleLogout}
        onShowSettings={() => {}}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: /logout/i }));
    expect(handleLogout).toHaveBeenCalledTimes(1);
  });
});
