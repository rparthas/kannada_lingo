use serde::de::DeserializeOwned;
use tauri::{
  plugin::{PluginApi, PluginHandle},
  AppHandle, Runtime,
};

use crate::models::*;

#[cfg(target_os = "ios")]
tauri::ios_plugin_binding!(init_plugin_native_audio);

pub fn init<R: Runtime, C: DeserializeOwned>(
  _app: &AppHandle<R>,
  api: PluginApi<R, C>,
) -> crate::Result<NativeAudio<R>> {
  #[cfg(target_os = "android")]
  let handle = api.register_android_plugin("", "NativeAudioPlugin")?;
  #[cfg(target_os = "ios")]
  let handle = api.register_ios_plugin(init_plugin_native_audio)?;
  Ok(NativeAudio(handle))
}

/// Access to the native-audio APIs.
pub struct NativeAudio<R: Runtime>(PluginHandle<R>);

impl<R: Runtime> NativeAudio<R> {
  pub fn play_phrase(&self, request: PlayPhraseRequest) -> crate::Result<()> {
    self
      .0
      .run_mobile_plugin("playPhrase", request)
      .map_err(Into::into)
  }

  pub fn pause_playback(&self) -> crate::Result<()> {
    self
      .0
      .run_mobile_plugin("pausePlayback", ())
      .map_err(Into::into)
  }

  pub fn start_recording(&self) -> crate::Result<()> {
    self
      .0
      .run_mobile_plugin("startRecording", ())
      .map_err(Into::into)
  }

  pub fn stop_recording(&self) -> crate::Result<RecordingResult> {
    self
      .0
      .run_mobile_plugin("stopRecording", ())
      .map_err(Into::into)
  }

  pub fn play_learner_recording(
    &self,
    request: PlayLearnerRecordingRequest,
  ) -> crate::Result<()> {
    self
      .0
      .run_mobile_plugin("playLearnerRecording", request)
      .map_err(Into::into)
  }
}