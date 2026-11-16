import { useMemo, useState } from "react";
import type { ExerciseDto, LearningItemDto } from "../../services/api/tauri";
import {
  evaluateKannadaRecall,
  evaluateMultipleChoice,
  evaluateWordOrder,
  normalizeFreeText,
} from "../../domain/exercises/evaluate";

export interface ExerciseResult {
  isCorrect: boolean;
  response: Record<string, unknown>;
  selfAssessed?: boolean;
}

interface Props {
  exercise: ExerciseDto;
  onComplete: (result: ExerciseResult) => void;
}

function PhraseCard({ item }: { item: LearningItemDto }) {
  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-stone-200">
      <p className="text-3xl font-semibold text-stone-900 kannada">{item.kannadaText}</p>
      <p className="mt-2 text-lg text-amber-800">{item.transliteration}</p>
      {item.contextNote ? (
        <p className="mt-3 text-sm text-stone-600">{item.contextNote}</p>
      ) : null}
    </div>
  );
}

export function ExerciseRenderer({ exercise, onComplete }: Props) {
  const item = exercise.learningItem;
  const [revealed, setRevealed] = useState(false);
  const [textAnswer, setTextAnswer] = useState("");
  const [selected, setSelected] = useState<number | null>(null);
  const [tiles, setTiles] = useState<string[]>(
    () => (exercise.prompt.tiles as string[] | undefined)?.slice() ?? [],
  );
  const [built, setBuilt] = useState<string[]>([]);
  const [feedback, setFeedback] = useState<string | null>(null);

  const choices = useMemo(
    () => (exercise.prompt.choices as string[] | undefined) ?? [],
    [exercise.prompt.choices],
  );

  function submitMcq(correctIndex: number) {
    if (selected === null) return;
    const isCorrect = evaluateMultipleChoice(selected, correctIndex);
    setFeedback(isCorrect ? "Correct" : "Try reviewing the phrase.");
    onComplete({ isCorrect, response: { selected } });
  }

  if (!item && exercise.exerciseType !== "vocabulary_flashcard") {
    return <p className="text-stone-600">Exercise is missing phrase data.</p>;
  }

  const instruction = String(exercise.prompt.instruction ?? "Complete the exercise.");

  switch (exercise.exerciseType) {
    case "vocabulary_flashcard":
      if (!item) return null;
      return (
        <div className="space-y-4">
          <p className="text-stone-700">{instruction}</p>
          <PhraseCard item={item} />
          {!revealed ? (
            <button
              type="button"
              className="w-full rounded-xl bg-amber-500 py-3 font-semibold text-white"
              onClick={() => setRevealed(true)}
            >
              Reveal meaning
            </button>
          ) : (
            <div className="space-y-3">
              <p className="text-xl font-medium text-stone-900">{item.englishMeaning}</p>
              <button
                type="button"
                className="w-full rounded-xl bg-stone-900 py-3 font-semibold text-white"
                onClick={() =>
                  onComplete({ isCorrect: true, response: { revealed: true } })
                }
              >
                Continue
              </button>
            </div>
          )}
        </div>
      );

    case "listen_identify":
    case "kannada_to_english":
      if (!item) return null;
      return (
        <div className="space-y-4">
          <p className="text-stone-700">{instruction}</p>
          <PhraseCard item={item} />
          <div className="grid gap-2">
            {choices.map((choice, index) => (
              <button
                key={choice}
                type="button"
                className={`rounded-xl border px-4 py-3 text-left ${
                  selected === index ? "border-amber-500 bg-amber-50" : "border-stone-200"
                }`}
                onClick={() => setSelected(index)}
              >
                {choice}
              </button>
            ))}
          </div>
          <button
            type="button"
            className="w-full rounded-xl bg-amber-500 py-3 font-semibold text-white disabled:opacity-50"
            disabled={selected === null}
            onClick={() =>
              submitMcq(Number(exercise.prompt.correct_index ?? exercise.prompt.correctIndex))
            }
          >
            Check
          </button>
          {feedback ? <p className="text-sm text-stone-600">{feedback}</p> : null}
        </div>
      );

    case "english_to_kannada":
      if (!item) return null;
      return (
        <div className="space-y-4">
          <p className="text-stone-700">{instruction}</p>
          <p className="text-xl font-medium">{item.englishMeaning}</p>
          <input
            className="w-full rounded-xl border border-stone-300 px-4 py-3 text-lg"
            value={textAnswer}
            onChange={(e) => setTextAnswer(e.target.value)}
            placeholder="Type Kannada or transliteration"
            autoCapitalize="off"
            autoCorrect="off"
          />
          <button
            type="button"
            className="w-full rounded-xl bg-amber-500 py-3 font-semibold text-white"
            onClick={() => {
              const isCorrect = evaluateKannadaRecall(textAnswer, {
                kannadaText: item.kannadaText,
                transliteration: item.transliteration,
                englishMeaning: item.englishMeaning,
                acceptedAnswers: item.acceptedAnswers,
              });
              setFeedback(isCorrect ? "Correct" : `Expected something like “${item.transliteration}”.`);
              onComplete({ isCorrect, response: { textAnswer } });
            }}
          >
            Check
          </button>
          {feedback ? <p className="text-sm text-stone-600">{feedback}</p> : null}
        </div>
      );

    case "fill_blank": {
      if (!item) return null;
      const accepted =
        (exercise.prompt.accepted as string[] | undefined) ?? [];
      const blanked = String(exercise.prompt.blanked_transliteration ?? "");
      return (
        <div className="space-y-4">
          <p className="text-stone-700">{instruction}</p>
          <p className="text-lg text-stone-800">{blanked}</p>
          <input
            className="w-full rounded-xl border border-stone-300 px-4 py-3"
            value={textAnswer}
            onChange={(e) => setTextAnswer(e.target.value)}
          />
          <button
            type="button"
            className="w-full rounded-xl bg-amber-500 py-3 font-semibold text-white"
            onClick={() => {
              const isCorrect = [item.transliteration, ...accepted].some(
                (v) => normalizeFreeText(textAnswer) === normalizeFreeText(v),
              );
              onComplete({ isCorrect, response: { textAnswer } });
            }}
          >
            Check
          </button>
        </div>
      );
    }

    case "sentence_construction": {
      const solution =
        (exercise.prompt.solution as string[] | undefined) ?? [];
      return (
        <div className="space-y-4">
          <p className="text-stone-700">{instruction}</p>
          <div className="min-h-12 rounded-xl border border-dashed border-stone-300 p-3">
            {built.length === 0 ? (
              <span className="text-stone-400">Tap words in order</span>
            ) : (
              built.join(" ")
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {tiles.map((tile) => (
              <button
                key={tile}
                type="button"
                className="rounded-full bg-stone-100 px-4 py-2 text-sm"
                onClick={() => {
                  setBuilt((prev) => [...prev, tile]);
                  setTiles((prev) => prev.filter((t) => t !== tile));
                }}
              >
                {tile}
              </button>
            ))}
          </div>
          <button
            type="button"
            className="w-full rounded-xl bg-amber-500 py-3 font-semibold text-white"
            onClick={() => {
              const isCorrect = evaluateWordOrder(built, solution);
              onComplete({ isCorrect, response: { built } });
            }}
          >
            Check order
          </button>
        </div>
      );
    }

    case "listen_repeat":
      if (!item) return null;
      return (
        <div className="space-y-4">
          <p className="text-stone-700">{instruction}</p>
          <PhraseCard item={item} />
          <p className="text-sm text-stone-500">
            Audio playback will use human recordings on device once assets are bundled.
          </p>
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: "Needs practice", ok: false, confident: false },
              { label: "Good", ok: true, confident: false },
              { label: "Easy", ok: true, confident: true },
            ].map((opt) => (
              <button
                key={opt.label}
                type="button"
                className="rounded-xl border border-stone-200 py-3 text-sm"
                onClick={() =>
                  onComplete({
                    isCorrect: opt.ok,
                    selfAssessed: opt.confident,
                    response: { selfGrade: opt.label },
                  })
                }
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      );

    default:
      return (
        <p className="text-stone-600">Unsupported exercise type: {exercise.exerciseType}</p>
      );
  }
}