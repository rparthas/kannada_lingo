import { useState } from "react";
import { tauriApi } from "../../services/api/tauri";

interface Props {
  onDone: () => void;
}

const GOAL_PRESETS = [
  { xp: 15, label: "Light — ~5 min/day" },
  { xp: 30, label: "Regular — ~10 min/day" },
  { xp: 50, label: "Intensive — ~15 min/day" },
] as const;

export function OnboardingScreen({ onDone }: Props) {
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [dailyGoalXp, setDailyGoalXp] = useState(30); // default to regular
  const [canReadScript, setCanReadScript] = useState(false);

  async function finish() {
    setBusy(true);
    try {
      await tauriApi.updateLearnerProfile(dailyGoalXp);
      await tauriApi.completeOnboarding(name.trim() || undefined);
      onDone();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-dvh flex-col justify-center bg-gradient-to-b from-amber-50 to-stone-100 px-6">
      <h1 className="text-3xl font-bold text-stone-900">Kannada Quest</h1>
      <p className="mt-3 text-stone-700">
        Learn practical spoken Bengaluru Kannada in short daily sessions.
      </p>

      <label className="mt-8 block text-sm font-medium text-stone-600">
        Your name (optional)
        <input
          className="mt-2 w-full rounded-xl border border-stone-300 bg-white px-4 py-3"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Learner"
        />
      </label>

      <fieldset className="mt-8 space-y-3">
        <legend className="text-sm font-medium text-stone-600">Daily goal</legend>
        <div className="grid grid-cols-3 gap-2">
          {GOAL_PRESETS.map((preset) => (
            <button
              key={preset.xp}
              type="button"
              onClick={() => setDailyGoalXp(preset.xp)}
              disabled={busy}
              className={`rounded-xl border-2 px-3 py-3 text-sm text-center transition-colors ${
                dailyGoalXp === preset.xp
                  ? "border-amber-500 bg-amber-50 text-amber-900"
                  : "border-stone-200 bg-white hover:border-amber-300"
              }`}
            >
              {preset.xp} XP
              <br />
              <span className="text-xs font-normal text-stone-500">
                {preset.label}
              </span>
            </button>
          ))}
        </div>
      </fieldset>

      <label className="mt-6 flex items-center gap-3 text-sm text-stone-600">
        <input
          type="checkbox"
          checked={canReadScript}
          onChange={(e) => setCanReadScript(e.target.checked)}
          className="rounded border-stone-300 text-amber-600 focus:ring-amber-500"
        />
        <span>
          I can read Kannada script — show script first in exercises
        </span>
      </label>

      <button
        type="button"
        disabled={busy}
        className="mt-8 rounded-xl bg-amber-500 py-3 text-lg font-semibold text-white disabled:opacity-60"
        onClick={() => void finish()}
      >
        Start learning
      </button>
    </div>
  );
}