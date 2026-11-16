import { StubAudioService } from "./types";
import { WebAudioService } from "./webAudioService";
import { isTauri } from "@tauri-apps/api/core";

export type { AudioService, AudioAssetRef, PlaybackSpeed, RecordingResult } from "./types";
export { loadAudioAssets, pickPlaybackAsset, assetRefFromDto } from "./webAudioService";

let singleton: WebAudioService | StubAudioService | null = null;

export function getAudioService(): WebAudioService | StubAudioService {
  if (!singleton) {
    singleton = isTauri() ? new WebAudioService() : new StubAudioService();
  }
  return singleton;
}