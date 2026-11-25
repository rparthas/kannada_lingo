use serde::de::DeserializeOwned;
use tauri::{plugin::PluginApi, AppHandle, Runtime};

use crate::models::*;

pub fn init<R: Runtime, C: DeserializeOwned>(
  app: &AppHandle<R>,
  _api: PluginApi<R, C>,
) -> crate::Result<NativeAudio<R>> {
  Ok(NativeAudio(app.clone()))
}

/// Desktop stub — phrase playback stays in the webview via `WebAudioService`.
pub struct NativeAudio<R: Runtime>(AppHandle<R>);

impl<R: Runtime> NativeAudio<R> {
  pub fn play_phrase(&self, _request: PlayPhraseRequest) -> crate::Result<()> {
    Err(crate::Error::UnsupportedPlatform)
  }

  pub fn pause_playback(&self) -> crate::Result<()> {
    Err(crate::Error::UnsupportedPlatform)
  }

  pub fn start_recording(&self) -> crate::Result<()> {
    Err(crate::Error::UnsupportedPlatform)
  }

  pub fn stop_recording(&self) -> crate::Result<RecordingResult> {
    Err(crate::Error::UnsupportedPlatform)
  }

  pub fn play_learner_recording(
    &self,
    _request: PlayLearnerRecordingRequest,
  ) -> crate::Result<()> {
    Err(crate::Error::UnsupportedPlatform)
  }
}