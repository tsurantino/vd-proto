# Frontend Refactoring Guide

## ✅ Backend Complete!

**Before:** 2,025 lines
**After:** 375 lines
**Reduction:** 81.5% ✨

All backend modules created and working. Now complete the frontend:

---

## 🎯 Frontend JavaScript Extraction

### Current State
- `index.html.backup` - Original 1,373 line file (backed up)
- `index.html` - Needs to be refactored
- All JS is currently inline in `<script>` tags

### Target State
```
web/
├── index.html (~250 lines - clean HTML only)
├── styles.css (✓ exists)
├── manifest.json (✓ exists)
└── js/
    ├── main.js
    ├── config/scenes.js
    ├── core/
    │   ├── socket.js
    │   ├── params.js
    │   └── session.js
    └── ui/
        ├── status.js
        ├── sliders.js
        ├── buttons.js
        ├── colors.js
        └── tabs.js
```

---

## 📝 Implementation Instructions

### Step 1: Extract Scene Configuration

**File:** `js/config/scenes.js`

Extract lines 597-756 from `index.html.backup` (the `sceneConfig` object):

```javascript
// Scene parameter configuration
export const sceneConfig = {
    shapeMorph: {
        enabled: ['size', 'density', 'scaling_amount', ...],
        enabledTabs: ['scale', 'rotation', 'translation', ...],
        defaults: { size: 1.2, density: 0.6, ... },
        tooltips: { size: 'Controls shape size', ... }
    },
    waveField: { ... },
    particleFlow: { ... },
    procedural: { ... },
    grid: { ... },
    illusions: { ... }
};
```

### Step 2: Create Core Modules

**File:** `js/core/socket.js`

```javascript
// WebSocket connection management
export class SocketManager {
    constructor() {
        this.socket = io(window.location.origin);
        this.setupListeners();
    }

    setupListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateStatus('connected');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateStatus('disconnected');
        });

        this.socket.on('status', (data) => this.handleStatus(data));
        this.socket.on('stats', (data) => this.handleStats(data));
    }

    sendParams(params) {
        const flatParams = {...params, ...params.scene_params};
        this.socket.emit('update_params', flatParams);
    }

    updateStatus(status) {
        const el = document.getElementById('connection-status');
        el.textContent = status === 'connected' ? 'Connected' : 'Disconnected';
        el.className = `status-value ${status}`;
    }

    handleStatus(data) {
        if (data.config) {
            document.getElementById('grid-size').textContent =
                `${data.config.gridX}×${data.config.gridY}×${data.config.gridZ}`;
        }
    }

    handleStats(data) {
        document.getElementById('fps').textContent = data.fps;
        document.getElementById('active-leds').textContent = data.active_leds.toLocaleString();
    }
}
```

**File:** `js/core/params.js`

```javascript
// Parameter state management
export class ParamsManager {
    constructor() {
        this.params = {
            scene_type: 'shapeMorph',
            size: 1.0,
            density: 0.5,
            // ... all other default params from lines 762-812
            scene_params: {
                shape: 'sphere',
                waveType: 'ripple',
                pattern: 'particles',
                illusionType: 'infiniteCorridor',
                proceduralType: 'noise',
                gridPattern: 'full'
            }
        };
    }

    update(key, value) {
        if (this.params.hasOwnProperty(key)) {
            this.params[key] = value;
        } else {
            this.params.scene_params[key] = value;
        }
    }

    get(key) {
        return this.params[key] ?? this.params.scene_params[key];
    }
}
```

**File:** `js/core/session.js`

```javascript
// Session memory for per-scene parameters
export class SessionMemory {
    constructor() {
        this.memory = {};
    }

    save(sceneType, params) {
        this.memory[sceneType] = {...params};
    }

    load(sceneType) {
        return this.memory[sceneType] || null;
    }
}
```

### Step 3: Create UI Modules

**File:** `js/ui/sliders.js`

```javascript
// Slider setup and handling
export function setupSlider(id, param, decimals, paramsManager, socketManager, sessionMemory) {
    const slider = document.getElementById(id);
    const valueDisplay = document.getElementById(`${id}-value`);

    if (!slider || !valueDisplay) {
        console.warn(`Slider not found: ${id}`);
        return;
    }

    slider.addEventListener('input', (e) => {
        const value = parseFloat(e.target.value);
        valueDisplay.textContent = value.toFixed(decimals);
        paramsManager.update(param, value);

        // Mark as user-modified
        const sceneType = paramsManager.params.scene_type;
        if (!sessionMemory.memory[sceneType]) {
            sessionMemory.memory[sceneType] = {};
        }
        sessionMemory.memory[sceneType][param] = value;

        socketManager.sendParams(paramsManager.params);
    });
}
```

**File:** `js/ui/buttons.js`

```javascript
// Button group handling
export function setupButtonGroup(selector, paramName, paramsManager, socketManager) {
    document.querySelectorAll(selector).forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active from all buttons in this group
            document.querySelectorAll(selector).forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            paramsManager.update(paramName, btn.dataset.value);
            socketManager.sendParams(paramsManager.params);
        });
    });
}

export function setupToggleButton(id, paramName, paramsManager, socketManager) {
    const btn = document.getElementById(id);
    if (!btn) return;

    btn.addEventListener('click', () => {
        btn.classList.toggle('active');
        paramsManager.update(paramName, btn.classList.contains('active'));
        socketManager.sendParams(paramsManager.params);
    });
}
```

**File:** `js/ui/tabs.js`

```javascript
// Tab and subtab switching
export function switchSubtab(subtabName) {
    // Hide all subtab content
    document.querySelectorAll('.subtab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Remove active from all buttons
    document.querySelectorAll('.subtab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected subtab
    document.getElementById(`subtab-${subtabName}`)?.classList.add('active');
    document.querySelector(`.subtab-btn[data-subtab="${subtabName}"]`)?.classList.add('active');
}

export function setupSubtabs() {
    document.querySelectorAll('.subtab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            if (!btn.classList.contains('disabled')) {
                switchSubtab(btn.dataset.subtab);
            }
        });
    });
}
```

**File:** `js/ui/colors.js`

```javascript
// Color preset handling
export function setupColorPresets(paramsManager, socketManager) {
    document.querySelectorAll('.color-preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const type = btn.dataset.type;

            // Remove active from all color buttons
            document.querySelectorAll('.color-preset-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            if (type === 'single') {
                paramsManager.params.color_mode = 'base';
                paramsManager.params.color_type = 'single';
                paramsManager.params.color_single = btn.dataset.color;
            } else if (type === 'gradient') {
                paramsManager.params.color_mode = 'base';
                paramsManager.params.color_type = 'gradient';
                paramsManager.params.color_gradient = btn.dataset.gradient;
            } else if (type === 'rainbow') {
                paramsManager.params.color_mode = 'rainbow';
            }

            socketManager.sendParams(paramsManager.params);
        });
    });
}

export function setupEffectButtons(paramsManager, socketManager) {
    document.querySelectorAll('button[data-effect]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('button[data-effect]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            paramsManager.params.color_effect = btn.dataset.effect;
            socketManager.sendParams(paramsManager.params);
        });
    });
}
```

### Step 4: Create Main Entry Point

**File:** `js/main.js`

```javascript
import { sceneConfig } from './config/scenes.js';
import { SocketManager } from './core/socket.js';
import { ParamsManager } from './core/params.js';
import { SessionMemory } from './core/session.js';
import { setupSlider } from './ui/sliders.js';
import { setupButtonGroup, setupToggleButton } from './ui/buttons.js';
import { setupSubtabs } from './ui/tabs.js';
import { setupColorPresets, setupEffectButtons } from './ui/colors.js';

// Initialize systems
const socketManager = new SocketManager();
const paramsManager = new ParamsManager();
const sessionMemory = new SessionMemory();

// Setup all sliders
setupSlider('size', 'size', 2, paramsManager, socketManager, sessionMemory);
setupSlider('density', 'density', 2, paramsManager, socketManager, sessionMemory);
setupSlider('animationSpeed', 'animationSpeed', 2, paramsManager, socketManager, sessionMemory);
// ... setup all other sliders

// Setup buttons
setupButtonGroup('[data-param="shape"]', 'shape', paramsManager, socketManager);
setupButtonGroup('[data-param="waveType"]', 'waveType', paramsManager, socketManager);
// ... setup all other button groups

// Setup toggles
setupToggleButton('invert', 'invert', paramsManager, socketManager);
setupToggleButton('scrolling_loop', 'scrolling_loop', paramsManager, socketManager);
// ... setup other toggles

// Setup UI components
setupSubtabs();
setupColorPresets(paramsManager, socketManager);
setupEffectButtons(paramsManager, socketManager);

console.log('Controller UI loaded');
```

### Step 5: Create Clean index.html

Replace `index.html` with clean version:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>Volumetric Display Controller</title>

    <!-- PWA iOS Support -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="VD Controller">
    <meta name="theme-color" content="#1a1a2e">

    <!-- PWA Manifest -->
    <link rel="manifest" href="/scenes/interactive/web/manifest.json">

    <!-- iOS Icons -->
    <link rel="apple-touch-icon" href="/scenes/interactive/web/icon-192.png">
    <link rel="apple-touch-icon" sizes="152x152" href="/scenes/interactive/web/icon-152.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/scenes/interactive/web/icon-180.png">
    <link rel="apple-touch-icon" sizes="167x167" href="/scenes/interactive/web/icon-167.png">

    <link rel="stylesheet" href="/scenes/interactive/web/styles.css">
</head>
<body>
    <div class="container">
        <!-- Status Panel -->
        <div id="status" class="panel">
            <div class="status-item">
                <span class="status-label">Status:</span>
                <span id="connection-status" class="status-value disconnected">Disconnected</span>
            </div>
            <div class="status-item">
                <span class="status-label">FPS:</span>
                <span id="fps" class="status-value">0</span>
            </div>
            <div class="status-item">
                <span class="status-label">Active LEDs:</span>
                <span id="active-leds" class="status-value">0</span>
            </div>
            <div class="status-item">
                <span class="status-label">Grid:</span>
                <span id="grid-size" class="status-value">0×0×0</span>
            </div>
        </div>

        <!-- COPY ALL THE HTML CONTROLS FROM ORIGINAL FILE (lines 46-589) -->
        <!-- Keep all the panels, buttons, sliders exactly as they are -->
        <!-- Just remove the <script> section entirely -->

    </div>

    <!-- Socket.io -->
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

    <!-- Our modular JavaScript -->
    <script type="module" src="/scenes/interactive/web/js/main.js"></script>
</body>
</html>
```

---

## ⚠️ Important Notes

1. **Keep all HTML controls** - Don't change any `<div class="panel">`, `<button>`, `<input>` elements
2. **Only remove `<script>`** - Delete the inline JavaScript (lines 591-1371)
3. **Use ES6 modules** - All new .js files should use `export`/`import`
4. **Test incrementally** - Create one module at a time and test

---

## 🧪 Testing Checklist

- [ ] Server starts without errors
- [ ] WebSocket connects (status shows "Connected")
- [ ] All sliders work and send updates
- [ ] All buttons work (scene selection, colors, effects)
- [ ] Tab switching works
- [ ] Scene parameters persist when switching scenes
- [ ] All 6 scene types render correctly
- [ ] Color effects work
- [ ] Global effects work (strobe, pulse, decay, invert)
- [ ] Scrolling masks work (all 11 patterns)

---

## 🚀 Quick Start

1. Extract scene config to `js/config/scenes.js`
2. Create `js/main.js` with basic structure
3. Create one core module at a time (socket → params → session)
4. Create one UI module at a time (sliders → buttons → tabs → colors)
5. Update `index.html` to use `type="module"` script tag
6. Test!

---

**All backend code is complete and working!** Just need to move the JS from inline to modules.
