import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import LandingPage from "./LandingPage";

// Mock the child component to isolate LandingPage logic
vi.mock("../GoogleLoginButton/GoogleLoginButton", () => ({
  default: ({ onLoginSuccess, onLoginError }: any) => (
    <div>
      <button onClick={() => onLoginSuccess({ credential: "fake-token" })}>
        Mock Login Success
      </button>
      <button onClick={onLoginError}>Mock Login Error</button>
    </div>
  ),
}));

describe("LandingPage Component", () => {
  it("renders the welcome message and branding", () => {
    render(<LandingPage onLoginSuccess={() => {}} onLoginError={() => {}} />);

    expect(screen.getByText("TranslatAR")).toBeInTheDocument();
    expect(screen.getByText("Web Portal")).toBeInTheDocument();
    // Updated match to look for "sign in" instead of "log in"
    expect(screen.getByText(/sign in to access/i)).toBeInTheDocument();
  });

  it("calls onLoginSuccess when login succeeds", () => {
    const handleSuccess = vi.fn();
    render(
      <LandingPage onLoginSuccess={handleSuccess} onLoginError={() => {}} />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Mock Login Success" }));
    expect(handleSuccess).toHaveBeenCalledWith({ credential: "fake-token" });
  });

  it("calls onLoginError when login fails", () => {
    const handleError = vi.fn();
    render(
      <LandingPage onLoginSuccess={() => {}} onLoginError={handleError} />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Mock Login Error" }));
    expect(handleError).toHaveBeenCalled();
  });
});
