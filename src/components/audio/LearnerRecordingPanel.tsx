import { useState } from "react";
import { getAudioService } from "../../services/audio";

interface Props {
  onRecorded?: (filePath: string) => void;
}

export function LearnerRecordingPanel({ onRecorded }: Props) {
  const [recording, setRecording] = useState(false);
  const [lastPath, setLastPath] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function start() {
    setMessage(null);
    try {
      await getAudioService().startRecording();
      setRecording(true);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Could not start recording.");
    }
  }

  async function stop() {
    try {
      const result = await getAudioService().stopRecording();
      setLastPath(result.filePath);
      onRecorded?.(result.filePath);
      setMessage("Saved your take locally (not uploaded).");
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Could not save recording.");
    } finally {
      setRecording(false);
    }
  }

  async function playTake() {
    if (!lastPath) return;
    setMessage(null);
    try {
      await getAudioService().playLearnerRecording(lastPath);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Could not play your recording.");
    }
  }

  return (
    <div className="rounded-2xl border border-dashed border-stone-300 bg-stone-50 p-4 space-y-3">
      <p className="text-sm font-medium text-stone-800">Your pronunciation</p>
      <p className="text-xs text-stone-500">
        Microphone is used only while you record. MVP does not score pronunciation.
        On iPhone, playback pauses when the screen locks — keep the app in the
        foreground while you practice.
      </p>
      <div className="flex flex-wrap gap-2">
        {!recording ? (
          <button
            type="button"
            className="rounded-xl bg-stone-900 px-4 py-2 text-sm font-semibold text-white"
            onClick={() => void start()}
          >
            {lastPath ? "Record again" : "Record"}
          </button>
        ) : (
          <button
            type="button"
            className="rounded-xl bg-red-600 px-4 py-2 text-sm font-semibold text-white"
            onClick={() => void stop()}
          >
            Stop
          </button>
        )}
        {lastPath ? (
          <button
            type="button"
            className="rounded-xl border border-stone-200 px-4 py-2 text-sm disabled:opacity-50"
            disabled={recording}
            onClick={() => void playTake()}
          >
            Play my recording
          </button>
        ) : null}
      </div>
      {recording ? (
        <p className="text-sm text-red-700 animate-pulse">Recording…</p>
      ) : null}
      <p className="text-sm text-stone-600" aria-live="polite">
        {message}
      </p>
    </div>
  );
}