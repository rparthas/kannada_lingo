interface Props {
  feedback: string;
  isCorrect: boolean;
  explanation?: string;
  onContinue: () => void;
}

export function ExerciseContinueBar({
  feedback,
  isCorrect,
  explanation,
  onContinue,
}: Props) {
  return (
    <div
      className={`mt-4 space-y-3 rounded-2xl p-4 ${isCorrect ? "bg-emerald-50 ring-1 ring-emerald-200" : "bg-amber-50 ring-1 ring-amber-200"}`}
    >
      <p className="font-medium text-stone-900">{feedback}</p>
      {explanation ? <p className="text-sm text-stone-600">{explanation}</p> : null}
      <button
        type="button"
        className="w-full rounded-xl bg-stone-900 py-3 font-semibold text-white"
        onClick={onContinue}
      >
        Continue
      </button>
    </div>
  );
}