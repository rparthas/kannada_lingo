import { useCallback, useEffect, useRef, useState } from "react";
import {
  assetRefFromDto,
  getAudioService,
  loadAudioAssets,
  pickPlaybackAsset,
} from "../../services/audio";
import type { PlaybackSpeed } from "../../services/audio";
import type { AudioAssetDto } from "../../services/api/tauri";

interface Props {
  learningItemId: string;
  /** Hide human vs AI labels in minimal listening UI */
  compact?: boolean;
  autoPlay?: boolean;
  className?: string;
}

export function PhraseAudioControls({
  learningItemId,
  compact = false,
  autoPlay = false,
  className = "",
}: Props) {
  const [assets, setAssets] = useState<AudioAssetDto[]>([]);
  const [speed, setSpeed] = useState<PlaybackSpeed>("normal");
  const [playing, setPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadAudioAssets(learningItemId).then(setAssets);
  }, [learningItemId]);

  const play = useCallback(async () => {
    const dto = pickPlaybackAsset(assets, speed);
    const ref = dto ? assetRefFromDto(dto, speed) : null;
    if (!ref?.relativePath) {
      setError("No audio bundled for this phrase yet.");
      return;
    }
    setError(null);
    setPlaying(true);
    try {
      await getAudioService().play(ref, speed);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Playback failed");
    } finally {
      setPlaying(false);
    }
  }, [assets, speed]);

  const autoPlayed = useRef(false);
  useEffect(() => {
    if (autoPlay && assets.length > 0 && !autoPlayed.current) {
      autoPlayed.current = true;
      void play();
    }
  }, [autoPlay, assets, play]);

  const active = pickPlaybackAsset(assets, speed);
  const hasSlow =
    assets.some((a) => a.speakingSpeed === "slow") || Boolean(active);

  if (!assets.length) {
    return (
      <p className={`text-sm text-stone-500 ${className}`}>
        Audio will appear here once assets are imported.
      </p>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          className="rounded-xl bg-amber-500 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
          disabled={playing}
          onClick={() => void play()}
        >
          {playing ? "Playing…" : "Play"}
        </button>
        <button
          type="button"
          className="rounded-xl border border-stone-200 px-4 py-2 text-sm"
          onClick={() => void getAudioService().pause()}
        >
          Pause
        </button>
        <button
          type="button"
          className="rounded-xl border border-stone-200 px-4 py-2 text-sm"
          onClick={() => void play()}
        >
          Replay
        </button>
        {hasSlow ? (
          <div className="flex rounded-xl border border-stone-200 p-0.5 text-sm">
            {(["normal", "slow"] as const).map((s) => (
              <button
                key={s}
                type="button"
                className={`rounded-lg px-3 py-1.5 capitalize ${
                  speed === s ? "bg-stone-900 text-white" : "text-stone-700"
                }`}
                onClick={() => setSpeed(s)}
              >
                {s}
              </button>
            ))}
          </div>
        ) : null}
      </div>
      {!compact && active ? (
        <p className="text-xs text-stone-500">
          Source:{" "}
          <span className="font-medium capitalize text-stone-700">
            {active.source === "ai" ? "AI supplement" : "human recording"}
          </span>
          {active.speakingSpeed === "slow" ? " · slow take" : ""}
        </p>
      ) : null}
      {error ? <p className="text-sm text-amber-800">{error}</p> : null}
    </div>
  );
}