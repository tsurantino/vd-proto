#include "resources/icon.h"
#include "resources/icon_helper.h"
#include "absl/log/log.h"

#include <filesystem>
#include <string>

void SetIcon(std::string argv0) {
  // Try to find icon.png in several possible locations
  std::vector<std::string> possible_paths = {
    // Next to the executable
    std::filesystem::path(argv0).parent_path() / "icon.png",
    // In resources directory relative to executable
    std::filesystem::path(argv0).parent_path() / "resources" / "icon.png",
    // In source directory (for development)
    "resources/icon.png",
    // In current directory
    "icon.png"
  };

  std::string icon_path;
  for (const auto& path : possible_paths) {
    if (std::filesystem::exists(path)) {
      icon_path = path;
      break;
    }
  }

  if (icon_path.empty()) {
    LOG(WARNING) << "Icon file not found in any of the expected locations";
    return;
  }

  LOG(INFO) << "Using icon from: " << icon_path;
  SetIconHelper(icon_path);
}