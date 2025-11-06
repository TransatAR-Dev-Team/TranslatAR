// src/components/SettingsModal/SettingsModal.test.tsx

import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import SettingsModal, { type Settings } from "./SettingsMenu";

describe("SettingsModal Component", () => {
  const mockSettings: Settings = {
    source_language: "en",
    target_language: "es",
    chunk_duration_seconds: 8.0,
    target_sample_rate: 48000,
    silence_threshold: 0.01,
    chunk_overlap_seconds: 0.5,
    websocket_url: "ws://localhost:8000/ws",
  };

  it("renders with the initial settings values", () => {
    render(
      <SettingsModal
        initialSettings={mockSettings}
        onSave={() => {}}
        onClose={() => {}}
        error={null}
      />,
    );
    // Check if one of the form fields is correctly populated
    expect(screen.getByLabelText(/source language/i)).toHaveValue("en");
  });

  it("calls the onClose prop when the cancel button is clicked", () => {
    const handleClose = vi.fn();
    render(
      <SettingsModal
        initialSettings={mockSettings}
        onSave={() => {}}
        onClose={handleClose}
        error={null}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: /cancel/i }));
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it("calls the onSave prop with the updated settings when save is clicked", () => {
    const handleSave = vi.fn();
    render(
      <SettingsModal
        initialSettings={mockSettings}
        onSave={handleSave}
        onClose={() => {}}
        error={null}
      />,
    );

    const sourceLangSelect = screen.getByLabelText(/source language/i);
    fireEvent.change(sourceLangSelect, { target: { value: "fr" } });

    fireEvent.click(screen.getByRole("button", { name: /save settings/i }));

    // Check that onSave was called with the new value
    expect(handleSave).toHaveBeenCalledTimes(1);
    expect(handleSave).toHaveBeenCalledWith(
      expect.objectContaining({
        source_language: "fr",
      }),
    );
  });

  it("displays an error message when an error is provided", () => {
    render(
      <SettingsModal
        initialSettings={mockSettings}
        onSave={() => {}}
        onClose={() => {}}
        error="Failed to save."
      />,
    );
    expect(screen.getByText(/failed to save/i)).toBeInTheDocument();
  });
});
