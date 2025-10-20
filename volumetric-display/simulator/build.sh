#!/bin/bash

# Build script for Volumetric Display C++ Simulator
# For macOS (tested on M3 Pro)

set -e  # Exit on error

echo "🔨 Building Volumetric Display C++ Simulator"
echo "============================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create build directory if it doesn't exist
if [ ! -d "build" ]; then
    echo "📁 Creating build directory..."
    mkdir -p build
fi

cd build

# Determine build type (default to Release)
BUILD_TYPE="${1:-Release}"
echo "🎯 Build type: $BUILD_TYPE"
echo ""

# Configure with CMake
echo "⚙️  Configuring with CMake..."
cmake -DCMAKE_BUILD_TYPE=$BUILD_TYPE ..

echo ""
echo "🔧 Building..."

# Build using all available cores
NUM_CORES=$(sysctl -n hw.ncpu)
echo "   Using $NUM_CORES CPU cores for parallel build"
cmake --build . -j$NUM_CORES

echo ""
echo "✅ Build complete!"
echo ""
echo "📍 Executable location: $SCRIPT_DIR/build/volumetric_display"
echo ""
echo "🚀 To run:"
echo "   cd build"
echo "   ./volumetric_display --config=../display_config/hw_config_4.json"
echo ""
echo "   Or from volumetric-display directory:"
echo "   ./build/volumetric_display --config=display_config/hw_config_4.json"
echo ""
echo "📖 See BUILD_AND_RUN.md for more options and troubleshooting"
