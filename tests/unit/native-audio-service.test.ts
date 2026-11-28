import { beforeEach, describe, expect, it, vi } from "vitest";

const invokeMock = vi.hoisted(() => vi.fn());

vi.mock("@tauri-apps/api/core", () => ({
  invoke: (...args: unknown[]) => invokeMock(...args),
}));

import { NativeIosAudioService } from "../../src/services/audio/nativeIosAudioService";
import type { AudioAssetRef } from "../../src/services/audio/types";

const service = new NativeIosAudioService();

function asset(overrides: Partial<AudioAssetRef> = {}): AudioAssetRef {
  return {
    learningItemId: "item-1",
    relativePath: "content/audio/item-1-normal.wav",
    source: "tts",
    speakingSpeed: "normal",
    ...overrides,
  };
}

beforeEach(() => {
  invokeMock.mockReset();
  invokeMock.mockImplementation((command: string) => {
    if (command === "resolve_resource_path") {
      return Promise.resolve("/app/content/audio/item-1-normal.wav");
    }
    return Promise.resolve();
  });
});

describe("NativeIosAudioService.play", () => {
  it("resolves the bundled path and plays a normal take at normal rate", async () => {
    await service.play(asset(), "normal");

    expect(invokeMock).toHaveBeenNthCalledWith(1, "resolve_resource_path", {
      relativePath: "content/audio/item-1-normal.wav",
    });
    expect(invokeMock).toHaveBeenNthCalledWith(
      2,
      "plugin:native-audio|play_phrase",
      {
        request: {
          filePath: "/app/content/audio/item-1-normal.wav",
          speed: "normal",
        },
      },
    );
  });

  it("time-stretches a normal take when the learner chooses slow", async () => {
    await service.play(asset(), "slow");

    expect(invokeMock).toHaveBeenLastCalledWith(
      "plugin:native-audio|play_phrase",
      {
        request: {
          filePath: "/app/content/audio/item-1-normal.wav",
          speed: "slow",
        },
      },
    );
  });

  it("does not time-stretch an already-slow take", async () => {
    await service.play(asset({ speakingSpeed: "slow" }), "slow");

    expect(invokeMock).toHaveBeenLastCalledWith(
      "plugin:native-audio|play_phrase",
      {
        request: {
          filePath: "/app/content/audio/item-1-normal.wav",
          speed: "normal",
        },
      },
    );
  });

  it("does nothing when the asset has no bundled path", async () => {
    await service.play(asset({ relativePath: undefined }));

    expect(invokeMock).not.toHaveBeenCalled();
  });
});

describe("NativeIosAudioService recording", () => {
  it("starts and stops a recording, returning the native path and duration", async () => {
    invokeMock.mockImplementation((command: string) => {
      if (command === "plugin:native-audio|stop_recording") {
        return Promise.resolve({ filePath: "/docs/take.m4a", durationMs: 1250 });
      }
      return Promise.resolve();
    });

    await service.startRecording();
    const result = await service.stopRecording();

    expect(invokeMock).toHaveBeenNthCalledWith(
      1,
      "plugin:native-audio|start_recording",
      {},
    );
    expect(result).toEqual({ filePath: "/docs/take.m4a", durationMs: 1250 });
  });

  it("plays a learner take from its absolute path", async () => {
    await service.playLearnerRecording("/docs/take.m4a");

    expect(invokeMock).toHaveBeenCalledWith(
      "plugin:native-audio|play_learner_recording",
      { request: { filePath: "/docs/take.m4a" } },
    );
  });

  it("surfaces the native permission guidance to the caller", async () => {
    invokeMock.mockRejectedValue(
      new Error(
        "Microphone access is off. Open Settings → Kannada Quest and turn on Microphone, then try again.",
      ),
    );

    await expect(service.startRecording()).rejects.toThrow(
      "Microphone access is off",
    );
  });
});
