import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import GoogleLoginButton from "./GoogleLoginButton";

// Mock the actual GoogleLogin component from the library
vi.mock("@react-oauth/google", () => ({
  GoogleLogin: ({ onSuccess }: { onSuccess: () => void }) => (
    <button onClick={onSuccess}>Sign in with Google</button>
  ),
}));

describe("GoogleLoginButton Component", () => {
  it("renders the button and calls onLoginSuccess when clicked", () => {
    const handleLoginSuccess = vi.fn();
    render(
      <GoogleLoginButton
        onLoginSuccess={handleLoginSuccess}
        onLoginError={() => {}}
      />,
    );

    const button = screen.getByRole("button", { name: /sign in with google/i });
    expect(button).toBeInTheDocument();

    fireEvent.click(button);
    expect(handleLoginSuccess).toHaveBeenCalledTimes(1);
  });
});
