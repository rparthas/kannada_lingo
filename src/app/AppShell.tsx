import { useEffect, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { BottomNav } from "../components/navigation/BottomNav";
import { SettingsScreen } from "../features/backup/SettingsScreen";
import { LearnScreen } from "../features/curriculum/LearnScreen";
import { HomeScreen } from "../features/home/HomeScreen";
import { LessonPlayerScreen } from "../features/lessons/LessonPlayerScreen";
import { OnboardingScreen } from "../features/onboarding/OnboardingScreen";
import { PracticeScreen } from "../features/practice/PracticeScreen";
import { PhraseDetailScreen } from "../features/phrases/PhraseDetailScreen";
import { PhraseSearchScreen } from "../features/phrase-search/PhraseSearchScreen";
import { ProgressScreen } from "../features/progress/ProgressScreen";
import { tauriApi } from "../services/api/tauri";
import { configureAudioService } from "../services/audio";

function MainRoutes() {
  return (
  <>
    <Routes>
      <Route path="/" element={<HomeScreen />} />
      <Route path="/learn" element={<LearnScreen />} />
      <Route path="/practice" element={<PracticeScreen />} />
      <Route path="/progress" element={<ProgressScreen />} />
      <Route path="/lesson/:lessonId" element={<LessonPlayerScreen />} />
      <Route path="/phrase/:itemId" element={<PhraseDetailScreen />} />
      <Route path="/phrase-search" element={<PhraseSearchScreen />} />
      <Route path="/settings" element={<SettingsScreen />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
    <BottomNav />
  </>
  );
}

export function AppShell() {
  const [ready, setReady] = useState(false);
  const [onboarded, setOnboarded] = useState(false);

  useEffect(() => {
    async function boot() {
      try {
        await tauriApi.initApp();
        await configureAudioService();
      } catch {
        /* Vite-only web preview without Tauri */
      }
      try {
        const profile = await tauriApi.getLearnerProfile();
        setOnboarded(profile.onboardingComplete);
      } catch {
        setOnboarded(true);
      }
      setReady(true);
    }
    void boot();
  }, []);

  if (!ready) {
    return (
      <div className="flex min-h-dvh items-center justify-center text-stone-600">
        Loading…
      </div>
    );
  }

  if (!onboarded) {
    return <OnboardingScreen onDone={() => setOnboarded(true)} />;
  }

  return (
    <BrowserRouter>
      <div className="min-h-dvh bg-stone-50 text-stone-900">
        <MainRoutes />
      </div>
    </BrowserRouter>
  );
}