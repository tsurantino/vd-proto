# Volumetric Display Simulator Guide

## Configuration Files Overview

### `hw_config_4.json` - Hardware Configuration
- **Purpose**: For sending to actual hardware controllers
- **IPs**: Mix of localhost (127.0.0.1) and remote hardware IPs (2.0.99.x)
- **Use with**: Python sender to control physical hardware
- **Cannot use with**: C++ simulator (will fail to bind remote IPs)

### `sim_config_4_hwsim.json` - Simulator Configuration
- **Purpose**: For testing with C++ simulator on localhost
- **IPs**: All localhost (127.0.0.1) with unique ports
- **Use with**: C++ simulator + Python sender (both on same machine)
- **Emulates**: Same 2-controller-per-cube setup with orientation mappings

## Port Mapping

The simulator config uses these localhost ports:

| Cube | Position  | Main Port | Controller 1 Port | Controller 2 Port | Orientations |
|------|-----------|-----------|-------------------|-------------------|--------------|
| 0    | (0,0,0)   | 6454      | 6458              | 6459              | Default, -Y/Z/-X, -Y/Z/-X |
| 1    | (20,0,0)  | 6455      | 6460              | 6461              | Default, -Y/Z/-X, -Y/Z/-X |
| 2    | (0,20,0)  | 6456      | 6462              | 6463              | Default, -Y/Z/-X, -Y/Z/-X |
| 3    | (20,20,0) | 6457      | 6464              | 6465              | Default, Y/-X/Z, Y/-X/Z |

## Usage Examples

### Test 1: Simulator Only (Visual Check)

Start the simulator and verify it binds to all ports:

```bash
cd artnet
./build/simulator --config=sim_config_4_hwsim.json --alpha=0.7
```

Expected output:
```
I0000 ... Initializing 12 Art-Net listener threads...
I0000 ... Thread started for cube 0 on 127.0.0.1:6454
I0000 ... Thread started for cube 0 on 127.0.0.1:6458
I0000 ... Thread started for cube 0 on 127.0.0.1:6459
I0000 ... Thread started for cube 1 on 127.0.0.1:6455
... (and so on for all 12 listeners)
```

✅ Success: Window opens showing 4 cubes in a 2x2 grid
❌ Failure: "Failed to bind" or "Address already in use"

### Test 2: Simulator + Python Sender

**Terminal 1 - Start Simulator:**
```bash
cd artnet
./build/simulator --config=sim_config_4_hwsim.json --alpha=0.7
```

**Terminal 2 - Run Python Sender:**
```bash
cd artnet
python3 sender.py --config sim_config_4_hwsim.json --scene sphere_scene
```

You should see:
- Terminal 1: Log messages showing Art-Net packets being received
- Simulator window: Animated spheres bouncing in 3D
- All orientations correctly applied to each cube

### Test 3: Verify Orientation Mappings

1. Start simulator with axis display:
   ```bash
   ./build/simulator --config=sim_config_4_hwsim.json
   ```

2. Press 'A' to show axes

3. Verify each cube shows:
   - **World axes** (large, bottom-left corner)
   - **Per-cube axes** (small, per-cube origin)

4. Run a simple test pattern:
   ```bash
   # In another terminal
   python3 sender.py --config sim_config_4_hwsim.json \
     --scene sphere_scene --debug
   ```

5. Observe that:
   - Cube 0 (bottom-left): Standard orientation
   - Cube 1 (bottom-right): Standard orientation
   - Cube 2 (top-left): Standard orientation
   - Cube 3 (top-right): Different orientation (Y/-X/Z)

### Test 4: Interactive Web Scene

**Terminal 1:**
```bash
./build/simulator --config=sim_config_4_hwsim.json --alpha=0.7
```

**Terminal 2:**
```bash
python3 interactive_scene_server.py --config sim_config_4_hwsim.json
```

**Browser:**
Open http://localhost:5001 and control the 3D scene in real-time!

## Troubleshooting

### Error: "Address already in use"

Another process is using the ports. Find and kill it:

```bash
# Find processes using the ports
lsof -i :6454-6465

# Kill the simulator
pkill simulator

# Or kill specific port
lsof -ti :6454 | xargs kill
```

### Error: "Failed to bind socket"

Make sure you're using the simulator config:

```bash
# ❌ Wrong - will fail
./build/simulator --config=hw_config_4.json

# ✅ Correct - all localhost
./build/simulator --config=sim_config_4_hwsim.json
```

### Simulator shows no data

1. Check that Python sender is running
2. Verify config files match:
   ```bash
   # Both should use same config
   ./build/simulator --config=sim_config_4_hwsim.json
   python3 sender.py --config sim_config_4_hwsim.json
   ```

3. Check Art-Net packets are being sent:
   ```bash
   # Monitor traffic on localhost
   sudo tcpdump -i lo0 -n port 6454
   ```

## Converting Between Configs

### To use on hardware:
Use `hw_config_4.json` with Python sender only:
```bash
python3 sender.py --config hw_config_4.json
```

### To use with simulator:
Use `sim_config_4_hwsim.json` with both:
```bash
# Terminal 1
./build/simulator --config=sim_config_4_hwsim.json

# Terminal 2
python3 sender.py --config sim_config_4_hwsim.json
```

## Performance Tips

1. **Reduce alpha for better visibility:**
   ```bash
   ./build/simulator --config=sim_config_4_hwsim.json --alpha=0.5
   ```

2. **Enable auto-rotation:**
   ```bash
   ./build/simulator --config=sim_config_4_hwsim.json --rotate_rate=0,10,0
   ```

3. **Adjust voxel scale for performance:**
   ```bash
   # Smaller voxels = better performance
   ./build/simulator --config=sim_config_4_hwsim.json --voxel_scale=0.1
   ```

## What's Being Tested

This simulator configuration validates:

✅ **Per-mapping orientation transforms**
- Each Art-Net listener can have its own orientation
- Orientations like `["-Y", "Z", "-X"]` and `["Y", "-X", "Z"]` work correctly

✅ **Multi-controller per cube setup**
- Each cube receives data from 3 separate Art-Net streams
- Z-indices are correctly distributed across controllers

✅ **Coordinate transformation pipeline**
- Controller-local → World coordinates transformation
- Axis remapping (X→Y, Y→Z, etc.)
- Sign flips (negation handling)

✅ **Visual output matches hardware**
- What you see in simulator = what you'll see on physical display
- Orientation bugs caught before deploying to hardware

## Next Steps

Once you've verified the simulator works correctly:

1. Test all scenes with the simulator config
2. Compare visual output between simulator and hardware
3. Use simulator for rapid prototyping of new scenes
4. Deploy tested scenes to hardware with confidence!
