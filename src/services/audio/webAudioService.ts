import { convertFileSrc, invoke, isTauri } from "@tauri-apps/api/core";
import type {
  AudioAssetRef,
  AudioService,
  PlaybackSpeed,
  RecordingResult,
} from "./types";
import type { AudioAssetDto } from "../api/tauri";

let activeAudio: HTMLAudioElement | null = null;

async function resolvePlayableUrl(relativePath: string): Promise<string> {
  if (isTauri()) {
    const absolute = await invoke<string>("resolve_resource_path", {
      relativePath,
    });
    return convertFileSrc(absolute);
  }
  return `/${relativePath.replace(/^content\//, "content/")}`;
}

function pickAsset(
  assets: AudioAssetDto[],
  speed: PlaybackSpeed,
  preferSource?: "human" | "ai",
): AudioAssetDto | undefined {
  const approved = assets.filter((a) => a.relativePath);
  const human = approved.filter((a) => a.source === "human");
  const pool = preferSource === "ai" ? approved : human.length ? human : approved;
  const exact = pool.find((a) => a.speakingSpeed === speed);
  if (exact) return exact;
  if (speed === "slow") {
    return pool.find((a) => a.speakingSpeed === "slow") ?? pool[0];
  }
  return pool.find((a) => a.speakingSpeed === "normal") ?? pool[0];
}

export async function loadAudioAssets(learningItemId: string): Promise<AudioAssetDto[]> {
  if (!isTauri()) return [];
  return invoke<AudioAssetDto[]>("list_audio_assets", { learningItemId });
}

export class WebAudioService implements AudioService {
  private mediaRecorder: MediaRecorder | null = null;
  private recordChunks: BlobPart[] = [];
  private recordStartedAt = 0;

  async play(asset: AudioAssetRef, speed: PlaybackSpeed = "normal"): Promise<void> {
    if (!asset.relativePath) return;
    await this.pause();
    const url = await resolvePlayableUrl(asset.relativePath);
    const el = new Audio(url);
    el.playbackRate = speed === "slow" && asset.speakingSpeed === "normal" ? 0.82 : 1;
    activeAudio = el;
    await el.play();
  }

  async pause(): Promise<void> {
    if (!activeAudio) return;
    activeAudio.pause();
    activeAudio = null;
  }

  async startRecording(): Promise<void> {
    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error(
        "Microphone is unavailable in this environment. Test recording on a physical device.",
      );
    }
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.recordChunks = [];
    const mime =
      MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";
    this.mediaRecorder = new MediaRecorder(stream, { mimeType: mime });
    this.mediaRecorder.ondataavailable = (evt) => {
      if (evt.data.size > 0) this.recordChunks.push(evt.data);
    };
    this.recordStartedAt = Date.now();
    this.mediaRecorder.start();
  }

  async stopRecording(): Promise<RecordingResult> {
    if (!this.mediaRecorder) {
      throw new Error("No recording in progress.");
    }
    const recorder = this.mediaRecorder;
    await new Promise<void>((resolve) => {
      recorder.onstop = () => resolve();
      recorder.stop();
      recorder.stream.getTracks().forEach((t) => t.stop());
    });
    this.mediaRecorder = null;
    const blob = new Blob(this.recordChunks, { type: recorder.mimeType });
    const durationMs = Math.max(0, Date.now() - this.recordStartedAt);

    if (isTauri()) {
      const bytes = Array.from(new Uint8Array(await blob.arrayBuffer()));
      const meta = await invoke<{ filePath: string; durationMs: number }>(
        "write_learner_recording",
        { bytes },
      );
      return { filePath: meta.filePath, durationMs: meta.durationMs };
    }

    const filePath = URL.createObjectURL(blob);
    return { filePath, durationMs };
  }

  async playLearnerRecording(filePath: string): Promise<void> {
    await this.pause();
    const src = filePath.startsWith("blob:") || filePath.startsWith("http")
      ? filePath
      : convertFileSrc(filePath);
    const el = new Audio(src);
    activeAudio = el;
    await el.play();
  }
}

export function assetRefFromDto(
  dto: AudioAssetDto,
  speed: PlaybackSpeed,
): AudioAssetRef | null {
  if (!dto.relativePath) return null;
  return {
    learningItemId: dto.learningItemId,
    relativePath: dto.relativePath,
    source: dto.source === "ai" ? "ai" : "human",
    speakingSpeed: (dto.speakingSpeed as PlaybackSpeed) ?? speed,
  };
}

export function pickPlaybackAsset(
  assets: AudioAssetDto[],
  speed: PlaybackSpeed,
): AudioAssetDto | undefined {
  return pickAsset(assets, speed);
}