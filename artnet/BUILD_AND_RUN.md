# Building and Running the Volumetric Display C++ Simulator

This guide explains how to build and run the volumetric display simulator on macOS (tested on M3 Pro).

## Prerequisites

### 1. Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Required Dependencies

```bash
# Install all required libraries via Homebrew
brew install cmake
brew install glfw
brew install glew
brew install glm
brew install boost
brew install abseil
brew install nlohmann-json
```

### 3. Verify Installation

```bash
# Check that the packages are installed
brew list | grep -E "cmake|glfw|glew|glm|boost|abseil|nlohmann-json"
```

You should see all these packages listed.

## Building the Simulator

### Step 1: Navigate to the artnet directory

```bash
cd /Users/tsurantino/Documents/projects/vd-proto/artnet
```

### Step 2: Create a build directory

```bash
mkdir -p build
cd build
```

### Step 3: Configure with CMake

```bash
# For Release build (optimized, recommended)
cmake -DCMAKE_BUILD_TYPE=Release ..

# OR for Debug build (with debugging symbols)
# cmake -DCMAKE_BUILD_TYPE=Debug ..
```

If you encounter any issues finding packages, you can explicitly set the Homebrew prefix:

```bash
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=/opt/homebrew ..
```

### Step 4: Build the executable

```bash
cmake --build . -j$(sysctl -n hw.ncpu)
```

The `-j$(sysctl -n hw.ncpu)` flag uses all available CPU cores for faster compilation.

### Step 5: Verify the build

```bash
ls -lh volumetric_display
```

You should see the `volumetric_display` executable.

## Running the Simulator

### Basic Usage

From the `build` directory:

```bash
./volumetric_display --config=../hw_config_4.json
```

Or from the `artnet` directory:

```bash
./build/volumetric_display --config=hw_config_4.json
```

### Command-Line Options

The simulator supports several command-line flags:

```bash
./volumetric_display \
  --config=hw_config_4.json \
  --alpha=0.5 \
  --layer_span=1 \
  --rotate_rate=0,10,0 \
  --color_correction=false \
  --voxel_scale=0.15 \
  --universes_per_layer=3
```

#### Available Flags:

- `--config` (string): Path to the configuration JSON file
  - Default: `"sim_config.json"`
  - Example: `--config=hw_config_4.json`

- `--alpha` (float): Alpha/opacity value for voxel rendering
  - Default: `0.5`
  - Range: `0.0` (transparent) to `1.0` (opaque)

- `--layer_span` (int): Layer span for z-axis sampling
  - Default: `1` (1:1 mapping)
  - Higher values skip layers (e.g., 2 = every other layer)

- `--rotate_rate` (string): Continuous rotation rate in degrees/second
  - Default: `"0,0,0"` (no rotation)
  - Format: `"X,Y,Z"`
  - Example: `"0,10,0"` (rotate 10°/sec around Y-axis)

- `--color_correction` (bool): Enable WS2812B color correction
  - Default: `false`
  - Use `--color_correction=true` to enable

- `--voxel_scale` (float): Size scaling for individual voxels
  - Default: `0.15`
  - Smaller values create gaps between voxels

- `--universes_per_layer` (int): Number of Art-Net universes per layer
  - Default: `3`
  - Should match your hardware configuration

### Interactive Controls

Once the simulator is running:

#### Keyboard:
- **A**: Toggle axis display (shows X/Y/Z axes)
- **B**: Toggle wireframe bounding boxes

#### Mouse:
- **Left Click + Drag**: Rotate the view
- **Shift + Left Click + Drag**: Pan the view
- **Scroll Wheel**: Zoom in/out

## Running with Python Sender

### Terminal 1: Start the C++ Simulator

```bash
cd /Users/tsurantino/Documents/projects/vd-proto/artnet
./build/volumetric_display --config=hw_config_4.json --alpha=0.7
```

### Terminal 2: Run the Python Sender

```bash
cd /Users/tsurantino/Documents/projects/vd-proto/artnet
python3 interactive_scene_server.py --config hw_config_4.json
```

The simulator will receive Art-Net data from the Python sender and display it in 3D with the correct orientations!

## Troubleshooting

### "Cannot find package" errors during CMake

Make sure Homebrew is properly configured:

```bash
# For Apple Silicon Macs
eval "$(/opt/homebrew/bin/brew shellenv)"

# Verify Homebrew prefix
echo $HOMEBREW_PREFIX
# Should output: /opt/homebrew
```

Then try configuring again:

```bash
cd build
rm -rf *  # Clean the build directory
cmake -DCMAKE_PREFIX_PATH=/opt/homebrew ..
```

### "Symbol not found" or linking errors

This usually means library versions are mismatched. Reinstall the dependencies:

```bash
brew reinstall glfw glew glm boost abseil nlohmann-json
```

Then rebuild:

```bash
cd build
rm -rf *
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . -j$(sysctl -n hw.ncpu)
```

### "Address already in use" error

If the Art-Net ports are already bound, make sure no other instance is running:

```bash
# Find processes using Art-Net default port
lsof -i :6454

# Kill any running instances
pkill volumetric_display
```

### Simulator window doesn't open

Make sure you have graphics support:

```bash
# Check OpenGL version
system_profiler SPDisplaysDataType | grep -i opengl
```

Your Mac M3 Pro should support OpenGL 4.1+.

## Clean Build

If you need to completely rebuild from scratch:

```bash
cd /Users/tsurantino/Documents/projects/vd-proto/artnet
rm -rf build
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . -j$(sysctl -n hw.ncpu)
```

## Testing Orientation Handling

To verify that orientations are correctly implemented:

1. Start the simulator with axis display enabled:
   ```bash
   ./build/volumetric_display --config=hw_config_4.json
   ```

2. Press 'A' to show axes - you should see:
   - **Red axis**: X direction
   - **Green axis**: Y direction
   - **Blue axis**: Z direction

3. Each cube should have its own axis widget showing its orientation

4. Run the Python sender with a simple test scene to verify the output matches between hardware and simulator

## Next Steps

- The simulator is now ready to receive Art-Net data from your Python sender
- All orientation transformations from `hw_config_4.json` are properly applied
- The visual output should match what you see on the physical hardware
