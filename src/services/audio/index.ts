import { invoke, isTauri } from "@tauri-apps/api/core";
import { NativeIosAudioService } from "./nativeIosAudioService";
import { resolveAudioServiceKind } from "./platform";
import { StubAudioService, type AudioService } from "./types";
import { WebAudioService } from "./webAudioService";

export type { AudioService, AudioAssetRef, PlaybackSpeed, RecordingResult } from "./types";
export { loadAudioAssets, pickPlaybackAsset, assetRefFromDto } from "./webAudioService";
export { resolveAudioServiceKind } from "./platform";

let singleton: AudioService | null = null;

/** Called during app boot before the learner can tap Play. */
export async function configureAudioService(): Promise<void> {
  if (!isTauri() || singleton) return;
  const platform = await invoke<string>("get_app_platform");
  const kind = resolveAudioServiceKind({ isTauri: true, platform });
  if (kind === "native-ios") {
    singleton = new NativeIosAudioService();
  } else {
    singleton = new WebAudioService();
  }
}

export function getAudioService(): AudioService {
  if (!singleton) {
    singleton = isTauri() ? new WebAudioService() : new StubAudioService();
  }
  return singleton;
}

/** @internal Tests only — reset module singleton. */
export function resetAudioServiceForTests(): void {
  singleton = null;
}