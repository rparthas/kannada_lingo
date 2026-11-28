// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { ExerciseRenderer } from "../../src/components/exercises/ExerciseRenderer";
import type { ExerciseDto, LearningItemDto } from "../../src/services/api/tauri";

const item: LearningItemDto = {
  id: "item-dhanyavada",
  kannadaText: "ಧನ್ಯವಾದ",
  transliteration: "dhanyavāda",
  englishMeaning: "Thank you",
  acceptedAnswers: ["thank you", "thanks"],
};

function exercise(overrides: Partial<ExerciseDto> = {}): ExerciseDto {
  return {
    id: "exercise-1",
    exerciseType: "kannada_to_english",
    learningItemId: item.id,
    prompt: {
      instruction: "What does this mean?",
      choices: ["Thank you", "Sorry"],
      correct_index: 0,
    },
    learningItem: item,
    ...overrides,
  };
}

afterEach(cleanup);

describe("ExerciseRenderer submit slot", () => {
  it("replaces Check with Continue after the answer is checked", () => {
    const onComplete = vi.fn();
    render(<ExerciseRenderer exercise={exercise()} onComplete={onComplete} />);

    expect(screen.queryByRole("button", { name: "Continue" })).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Thank you" }));
    fireEvent.click(screen.getByRole("button", { name: "Check" }));

    expect(screen.queryByRole("button", { name: "Check" })).toBeNull();
    expect(screen.getByText("Correct")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Continue" }));
    expect(onComplete).toHaveBeenCalledWith({
      isCorrect: true,
      response: { selected: 0 },
    });
  });

  it("does not leave a disabled Check next to Continue for typed answers", () => {
    const onComplete = vi.fn();
    render(
      <ExerciseRenderer
        exercise={exercise({
          exerciseType: "english_to_kannada",
          prompt: { instruction: "Say thank you in Kannada" },
        })}
        onComplete={onComplete}
      />,
    );

    fireEvent.change(screen.getByPlaceholderText("Type Kannada or transliteration"), {
      target: { value: "dhanyavada" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Check" }));

    expect(screen.queryByRole("button", { name: "Check" })).toBeNull();
    expect(screen.getByRole("button", { name: "Continue" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Continue" }));
    expect(onComplete).toHaveBeenCalledWith({
      isCorrect: true,
      response: { textAnswer: "dhanyavada" },
    });
  });
});
