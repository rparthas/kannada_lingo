#[tauri::command]
pub fn get_app_platform() -> String {
  #[cfg(target_os = "ios")]
  {
    return "ios".into();
  }
  #[cfg(target_os = "macos")]
  {
    return "macos".into();
  }
  #[cfg(target_os = "windows")]
  {
    return "windows".into();
  }
  #[cfg(target_os = "linux")]
  {
    return "linux".into();
  }
  #[cfg(target_os = "android")]
  {
    return "android".into();
  }
  #[allow(unreachable_code)]
  "unknown".into()
}

#[cfg(test)]
mod tests {
  use super::*;

  #[test]
  fn get_app_platform_returns_known_desktop_family() {
    let platform = get_app_platform();
    assert!(!platform.is_empty());
    assert_ne!(platform, "unknown");
  }
}