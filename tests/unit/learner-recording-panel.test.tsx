// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";

const audio = vi.hoisted(() => ({
  startRecording: vi.fn(),
  stopRecording: vi.fn(),
  playLearnerRecording: vi.fn(),
}));

vi.mock("../../src/services/audio", () => ({
  getAudioService: () => audio,
}));

import { LearnerRecordingPanel } from "../../src/components/audio/LearnerRecordingPanel";

beforeEach(() => {
  audio.startRecording.mockReset().mockResolvedValue(undefined);
  audio.stopRecording
    .mockReset()
    .mockResolvedValue({ filePath: "/docs/take-1.m4a", durationMs: 1200 });
  audio.playLearnerRecording.mockReset().mockResolvedValue(undefined);
});

afterEach(cleanup);

async function recordOnce() {
  fireEvent.click(screen.getByRole("button", { name: "Record" }));
  await screen.findByRole("button", { name: "Stop" });
  fireEvent.click(screen.getByRole("button", { name: "Stop" }));
  return screen.findByRole("button", { name: "Play my recording" });
}

describe("LearnerRecordingPanel", () => {
  it("supports record → play → retry without losing the last take", async () => {
    render(<LearnerRecordingPanel />);

    const play = await recordOnce();
    expect(audio.startRecording).toHaveBeenCalledTimes(1);
    expect(audio.stopRecording).toHaveBeenCalledTimes(1);

    fireEvent.click(play);
    await waitFor(() =>
      expect(audio.playLearnerRecording).toHaveBeenCalledWith("/docs/take-1.m4a"),
    );

    fireEvent.click(screen.getByRole("button", { name: "Record again" }));
    await screen.findByRole("button", { name: "Stop" });
    expect(audio.startRecording).toHaveBeenCalledTimes(2);

    // The previous take stays replayable, but not while the mic is hot.
    expect(
      (screen.getByRole("button", { name: "Play my recording" }) as HTMLButtonElement)
        .disabled,
    ).toBe(true);
  });

  it("shows the native permission guidance and keeps the panel usable", async () => {
    audio.startRecording.mockRejectedValue(
      new Error(
        "Microphone access is off. Open Settings → Kannada Quest and turn on Microphone, then try again.",
      ),
    );
    render(<LearnerRecordingPanel />);

    fireEvent.click(screen.getByRole("button", { name: "Record" }));

    expect(
      await screen.findByText(/Open Settings → Kannada Quest/),
    ).toBeTruthy();
    expect(screen.getByRole("button", { name: "Record" })).toBeTruthy();
  });

  it("reports a failed stop and returns to the idle state", async () => {
    audio.stopRecording.mockRejectedValue(new Error("Could not save recording."));
    render(<LearnerRecordingPanel />);

    fireEvent.click(screen.getByRole("button", { name: "Record" }));
    await screen.findByRole("button", { name: "Stop" });
    fireEvent.click(screen.getByRole("button", { name: "Stop" }));

    expect(await screen.findByText("Could not save recording.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Record" })).toBeTruthy();
  });
});
