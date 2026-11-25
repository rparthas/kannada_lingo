use tauri::{command, AppHandle, Runtime};

use crate::models::*;
use crate::NativeAudioExt;
use crate::Result;

#[command]
pub(crate) async fn play_phrase<R: Runtime>(
  app: AppHandle<R>,
  request: PlayPhraseRequest,
) -> Result<()> {
  app.native_audio().play_phrase(request)
}

#[command]
pub(crate) async fn pause_playback<R: Runtime>(app: AppHandle<R>) -> Result<()> {
  app.native_audio().pause_playback()
}

#[command]
pub(crate) async fn start_recording<R: Runtime>(app: AppHandle<R>) -> Result<()> {
  app.native_audio().start_recording()
}

#[command]
pub(crate) async fn stop_recording<R: Runtime>(app: AppHandle<R>) -> Result<RecordingResult> {
  app.native_audio().stop_recording()
}

#[command]
pub(crate) async fn play_learner_recording<R: Runtime>(
  app: AppHandle<R>,
  request: PlayLearnerRecordingRequest,
) -> Result<()> {
  app.native_audio().play_learner_recording(request)
}