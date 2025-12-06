import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import GoogleLoginButton from "./GoogleLoginButton";

// Mock that exposes both success and error triggers
vi.mock("@react-oauth/google", () => ({
  GoogleLogin: ({
    onSuccess,
    onError,
  }: {
    onSuccess: () => void;
    onError: () => void;
  }) => (
    <div>
      <button onClick={onSuccess}>Mock Success</button>
      <button onClick={onError}>Mock Error</button>
    </div>
  ),
}));

describe("GoogleLoginButton Component", () => {
  it("calls onLoginSuccess when success occurs", () => {
    const handleLoginSuccess = vi.fn();
    render(
      <GoogleLoginButton
        onLoginSuccess={handleLoginSuccess}
        onLoginError={() => {}}
      />,
    );

    fireEvent.click(screen.getByText("Mock Success"));
    expect(handleLoginSuccess).toHaveBeenCalledTimes(1);
  });

  it("calls onLoginError when error occurs", () => {
    const handleLoginError = vi.fn();
    // Mock alert so it doesn't pop up during test
    vi.spyOn(window, "alert").mockImplementation(() => {});
    vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <GoogleLoginButton
        onLoginSuccess={() => {}}
        onLoginError={handleLoginError}
      />,
    );

    fireEvent.click(screen.getByText("Mock Error"));
    expect(handleLoginError).toHaveBeenCalledTimes(1);
  });
});
