#!/bin/bash

# Installation script for Volumetric Display C++ Simulator dependencies
# For macOS (tested on M3 Pro)

set -e  # Exit on error

echo "🎨 Volumetric Display C++ Simulator - Dependency Installer"
echo "==========================================================="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew is not installed."
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Configure Homebrew for Apple Silicon
    if [[ $(uname -m) == 'arm64' ]]; then
        echo "🍎 Configuring Homebrew for Apple Silicon..."
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    echo "✅ Homebrew is already installed"
fi

echo ""
echo "📦 Installing required dependencies..."
echo ""

# List of required packages
PACKAGES=(
    "cmake"
    "glfw"
    "glew"
    "glm"
    "boost"
    "abseil"
    "nlohmann-json"
)

# Install each package
for package in "${PACKAGES[@]}"; do
    if brew list "$package" &>/dev/null; then
        echo "✅ $package is already installed"
    else
        echo "📦 Installing $package..."
        brew install "$package"
    fi
done

echo ""
echo "✅ All dependencies installed successfully!"
echo ""
echo "📊 Installed versions:"
echo "  CMake:          $(cmake --version | head -n1)"
echo "  Boost:          $(brew list --versions boost)"
echo "  Abseil:         $(brew list --versions abseil)"
echo ""
echo "🎯 Next steps:"
echo "  1. cd volumetric-display/simulator"
echo "  2. mkdir -p build && cd build"
echo "  3. cmake -DCMAKE_BUILD_TYPE=Release .."
echo "  4. cmake --build . -j\$(sysctl -n hw.ncpu)"
echo "  5. ./simulator --config=../display_config/hw_config_4.json"
echo ""
echo "📖 See simulator/BUILD_AND_RUN.md for detailed instructions"
