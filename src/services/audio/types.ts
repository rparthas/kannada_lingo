export type PlaybackSpeed = "normal" | "slow";

export interface AudioAssetRef {
  learningItemId: string;
  relativePath?: string;
  source: "human" | "ai" | "tts";
  speakingSpeed: PlaybackSpeed;
}

export interface RecordingResult {
  filePath: string;
  durationMs: number;
}

/** Platform adapter — implemented with native iOS APIs behind Tauri commands later. */
export interface AudioService {
  play(asset: AudioAssetRef, speed?: PlaybackSpeed): Promise<void>;
  pause(): Promise<void>;
  startRecording(): Promise<void>;
  stopRecording(): Promise<RecordingResult>;
  playLearnerRecording(filePath: string): Promise<void>;
}

export class StubAudioService implements AudioService {
  async play(): Promise<void> {}
  async pause(): Promise<void> {}
  async startRecording(): Promise<void> {
    throw new Error("Recording is only available inside the Tauri app.");
  }
  async stopRecording(): Promise<RecordingResult> {
    throw new Error("Recording is only available inside the Tauri app.");
  }
  async playLearnerRecording(): Promise<void> {}
}