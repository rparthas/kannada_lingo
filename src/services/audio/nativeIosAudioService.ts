import { invoke } from "@tauri-apps/api/core";
import type {
  AudioAssetRef,
  AudioService,
  PlaybackSpeed,
  RecordingResult,
} from "./types";

async function resolveAbsolutePath(relativePath: string): Promise<string> {
  return invoke<string>("resolve_resource_path", { relativePath });
}

function invokeNative<T>(command: string, args: Record<string, unknown> = {}): Promise<T> {
  return invoke<T>(`plugin:native-audio|${command}`, args);
}

export class NativeIosAudioService implements AudioService {
  async play(asset: AudioAssetRef, speed: PlaybackSpeed = "normal"): Promise<void> {
    if (!asset.relativePath) return;
    const filePath = await resolveAbsolutePath(asset.relativePath);
    // Only time-stretch normal takes. A "slow" recording is already slowed;
    // applying 0.82 again would play it at roughly half speed.
    const effectiveSpeed =
      speed === "slow" && asset.speakingSpeed === "normal" ? "slow" : "normal";
    await invokeNative("play_phrase", {
      request: { filePath, speed: effectiveSpeed },
    });
  }

  async pause(): Promise<void> {
    await invokeNative("pause_playback");
  }

  async startRecording(): Promise<void> {
    await invokeNative("start_recording");
  }

  async stopRecording(): Promise<RecordingResult> {
    const result = await invokeNative<{ filePath: string; durationMs: number }>(
      "stop_recording",
    );
    return { filePath: result.filePath, durationMs: result.durationMs };
  }

  async playLearnerRecording(filePath: string): Promise<void> {
    await invokeNative("play_learner_recording", {
      request: { filePath },
    });
  }
}