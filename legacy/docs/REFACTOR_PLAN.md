# Volumetric Control System - Refactoring Plan (Phases 1-3)

**Date Created:** 2025-10-17
**Status:** Planning Phase
**Priority:** High

---

## 🔴 Critical Issues Identified

### 1. **Incomplete Axis Controls** ✓ (User Confirmed)
- **Problem**: `translateY` is missing - you only have X and Z translation
- **Impact**: Cannot move objects up/down with oscillation
- **Location**: GlobalParameterMapper.js:248, main.js:240-243

### 2. **Architectural Confusion: Scenes vs. Illusions** ✓ (User Confirmed)
- **Problem**: Illusions are treated as separate from core scenes, but they use the same rendering pipeline
- **Design Issue**: No technical reason for separation - creates UI duplication and confusion
- **Files**: IllusionSceneLibrary.js (separate file), main.js (duplicate UI sections)
- **Recommendation**: Merge illusions into core SceneLibrary, add category tags instead

### 3. **Overlapping Concepts: Wave vs. Procedural vs. Plasma** ✓ (User Confirmed)
- **Wave Field**: Sine/cosine waves (ripple, plane, standing, interference)
- **Procedural**: Perlin noise with evolve/scroll animations
- **Plasma**: Multiple interfering sine waves (basically enhanced Wave)
- **Problem**: Plasma IS a wave effect - artificial separation
- **Location**: SceneLibrary.js:86-92 (Plasma scene)
- **Recommendation**: Merge Plasma into Wave Field as a new wave type

### 4. **Movement Effect Complexity** ✓ (User Confirmed)
- **Problem**: 10+ independent movement controls that stack unpredictably
- **Issues**:
  - Orbit + Ellipse + Spiral all do circular motion differently
  - Translate + Orbit + Figure-8 overlap conceptually
  - Wobble adds unpredictable rotation on top of manual rotation
  - No clear hierarchy or groups
- **Location**: main.js:228-289, GlobalParameterMapper.js:243-272
- **User Experience**: Very hard to achieve desired motion without trial-and-error

### 5. **Movement Effects Don't Apply to Wave/Procedural** ✓ (User Confirmed)
- **Problem**: Movement controls only work on shapeMorph and particleFlow
- **Location**: GlobalParameterMapper.js:17-47 (conditional application)
- **Gap**: Wave Field, Procedural, Vortex, Grid, Text3D, Plasma scenes can't use movement
- **Inconsistency**: Users expect global controls to work globally

### 6. **Parameter Mapping Confusion**
- **Problem**: Same UI control means different things per scene:
  - `size` → particleSize for particles, scale inverse for procedural
  - `amplitude` → wave amplitude OR threshold inverse for procedural
  - `animationSpeed` → velocity for particles, twist for vortex
- **Location**: GlobalParameterMapper.js:49-221
- **Impact**: Non-intuitive behavior when switching scenes

### 7. **Missing Parameter Automation UI Integration**
- Right-click automation exists but has poor discoverability
- No visual feedback on which parameters are automated while adjusting
- No preset automation patterns (e.g., "gentle sway", "pulsing grow")
- **Location**: main.js:1014-1188 (automation modal)

---

## ✅ Implementation Plan: Phases 1-3

---

## **PHASE 1: Fix Critical Gaps** (High Priority)

### ✅ Task 1.1: Add Missing translateY Control

**Files to modify:**
- `src/js/utils/GlobalParameterMapper.js`
- `src/js/main.js`
- `src/js/effects/SceneLibrary.js` (all shape functions)

**Changes:**

1. **GlobalParameterMapper.js**
   - Line 248: Add `translateY: 0` after `translateZ`
   - Line 23: Add `mapped.translateY = globalParams.translateY || 0;`
   - Line 282: Add `'translateY'` to movementParams array

2. **main.js**
   - After line 242 (translateZ control), add translateY slider:
   ```javascript
   createGlobalSliderControl('translateY', 'Translate Y Speed', display.getGlobalSceneParameter('translateY'), 0, 1, 0.05);
   ```

3. **SceneLibrary.js**
   - In each shape function (drawSphere, drawHelix, drawPlane, etc.), add translateY logic after line ~150:
   ```javascript
   if (params.translateY > 0 && params.translateAmplitude > 0) {
       centerY += Math.sin(offsetTime * params.translateY * 2) * (this.gridY * params.translateAmplitude * 0.3);
   }
   ```

**Testing:** Verify translateY slider appears and affects object vertical oscillation

---

### ✅ Task 1.2: Extend Movement Effects to All Scene Types

**Files to modify:**
- `src/js/utils/GlobalParameterMapper.js`
- `src/js/effects/SceneLibrary.js` (wave, procedural, vortex, grid, text3D renderers)

**Changes:**

1. **GlobalParameterMapper.js**
   - Lines 17-47: Change conditional from `if (sceneType === 'shapeMorph' || sceneType === 'particleFlow')` to apply to ALL scenes
   - Lines 294-305: Update `getActiveParameters()` to include movement params for all scene types

2. **SceneLibrary.js - renderWaveField()** (~line 45)
   - Add movement transformations to wave origin/direction
   - Apply rotation to wave direction vector
   - Apply translation offsets to wave phase

3. **SceneLibrary.js - renderProcedural()** (~line 57)
   - Apply scroll offsets to noise sampling coordinates
   - Apply rotation to noise space

4. **SceneLibrary.js - renderVortex()** (~line 65)
   - Add movement to vortex center position
   - Add rotation to vortex axis

5. **SceneLibrary.js - renderGrid()** (~line 71)
   - Apply transformations to grid origin
   - Rotate grid axes

6. **SceneLibrary.js - renderText3D()** (~line 78)
   - Apply full movement suite to text position/rotation

**Testing:** Verify rotation/translation controls affect non-shape scenes

---

### ✅ Task 1.3: Consolidate Circular Motion Controls (UI Organization)

**Files to modify:**
- `src/js/main.js`
- `src/css/styles.css`

**Changes:**

1. **main.js** - Reorganize lines 228-289 into collapsible groups:
   ```javascript
   // Basic Movement Section
   createSectionHeader('Basic Movement', 'basic-movement');
   // Rotation X/Y/Z
   // Translation X/Y/Z + Amplitude

   // Oscillation Section
   createSectionHeader('Oscillation', 'oscillation');
   // Bounce Speed/Height
   // Pulse Speed/Amount

   // Path Motion Section
   createSectionHeader('Path Motion', 'path-motion');
   // Orbit, Spiral, Figure-8, Ellipse

   // Advanced Section
   createSectionHeader('Advanced', 'advanced-movement');
   // Wobble, Scroll
   ```

2. **styles.css** - Add collapsible section styles:
   ```css
   .subsection-header {
       cursor: pointer;
       display: flex;
       justify-content: space-between;
       background: rgba(255,255,255,0.05);
       padding: 8px 10px;
       margin: 10px 0 5px 0;
       border-radius: 4px;
   }
   .subsection-content.collapsed {
       display: none;
   }
   ```

**Testing:** Verify sections collapse/expand, parameters grouped logically

---

## **PHASE 2: Architectural Refactoring** (Medium Priority)

### ✅ Task 2.1: Merge Illusions into Core SceneLibrary

**Files to modify:**
- `src/js/effects/SceneLibrary.js` (merge target)
- `src/js/effects/IllusionSceneLibrary.js` (DELETE after merge)
- `src/js/VolumetricDisplay.js` (remove separate illusion library)
- `src/js/main.js` (update UI to use categories)

**Changes:**

1. **SceneLibrary.js**
   - Add `category` field to all scene definitions:
     ```javascript
     'shapeMorph': {
         name: 'Shape Morph',
         category: 'core',
         defaultParams: { ... }
     }
     ```
   - Copy all 12 illusion scenes from IllusionSceneLibrary.js, set `category: 'illusion'`
   - Total scenes: 8 core + 12 illusions = 20 scenes

2. **VolumetricDisplay.js**
   - Remove IllusionSceneLibrary import and initialization
   - Remove `getIllusionSceneTypes()` method
   - Update `setScene()` to use single scene library

3. **main.js**
   - Lines 437-477: Keep "Core Scenes" section, filter by `category: 'core'`
   - Lines 730-776: Rename to "Illusion Scenes", filter by `category: 'illusion'`
   - Update button creation to use filtered scene lists

4. **IllusionSceneLibrary.js**
   - DELETE file after confirming all 12 scenes copied correctly

**Testing:** Verify all 20 scenes render correctly, UI grouped properly

---

### ✅ Task 2.2: Merge Plasma into Wave Field

**Files to modify:**
- `src/js/effects/SceneLibrary.js`
- `src/js/main.js`

**Changes:**

1. **SceneLibrary.js - renderWaveField()**
   - Add 'plasma' to waveType options (line 48):
     ```javascript
     waveType: 'ripple', // 'ripple', 'plane', 'standing', 'interference', 'plasma'
     ```
   - Move plasma rendering logic from renderPlasma() (lines 86-92) into renderWaveField() as case statement
   - Remove 'plasma' scene from createScenes() object
   - DELETE renderPlasma() function

2. **main.js - createWaveFieldControls()**
   - Update waveType select options (line 547):
     ```javascript
     { value: 'ripple', label: 'Ripple' },
     { value: 'plane', label: 'Plane' },
     { value: 'standing', label: 'Standing' },
     { value: 'interference', label: 'Interference' },
     { value: 'plasma', label: 'Plasma' }
     ```
   - Remove "Plasma" from scene type buttons (line 452)

**Testing:** Verify plasma effect accessible as wave type, original functionality preserved

---

### ✅ Task 2.3: Reorganize Movement Controls into Groups (Already in Task 1.3)

**Status:** Completed in Phase 1, Task 1.3

---

## **PHASE 3: UX Improvements** (Medium Priority)

### ✅ Task 3.1: Add Movement Presets

**Files to create:**
- `src/js/utils/MovementPresets.js` (NEW)

**Files to modify:**
- `src/js/main.js`
- `src/js/VolumetricDisplay.js`

**Changes:**

1. **Create MovementPresets.js**
   ```javascript
   export class MovementPresets {
       static presets = {
           'reset': {
               name: 'Reset All',
               params: { /* all movement params = 0 */ }
           },
           'gentleFloat': {
               name: 'Gentle Float',
               params: {
                   bounceSpeed: 0.2,
                   bounceHeight: 0.3,
                   translateX: 0.1,
                   translateZ: 0.15,
                   translateAmplitude: 0.2
               }
           },
           'orbitalDance': {
               name: 'Orbital Dance',
               params: {
                   orbitSpeed: 0.4,
                   orbitRadius: 0.5,
                   pulseSpeed: 0.3,
                   pulseAmount: 0.2,
                   rotationY: 0.3
               }
           },
           'tumbling': {
               name: 'Tumbling',
               params: {
                   wobbleSpeed: 0.6,
                   wobbleAmount: 0.7,
                   rotationX: 0.4,
                   rotationY: 0.5,
                   rotationZ: 0.3
               }
           },
           'figure8Glide': {
               name: 'Figure-8 Glide',
               params: {
                   figure8Speed: 0.5,
                   figure8Size: 0.6,
                   bounceSpeed: 0.2,
                   bounceHeight: 0.2
               }
           },
           'spiralAscent': {
               name: 'Spiral Ascent',
               params: {
                   spiralSpeed: 0.4,
                   spiralRadius: 0.5,
                   spiralHeight: 0.8,
                   rotationY: 0.3
               }
           }
       };

       static getPreset(name) { return this.presets[name]; }
       static getAll() { return Object.entries(this.presets); }
   }
   ```

2. **main.js**
   - Add preset buttons section after movement controls (~line 290):
   ```javascript
   const presetContainer = document.createElement('div');
   presetContainer.className = 'movement-presets';
   presetContainer.innerHTML = '<h4>Movement Presets</h4>';

   MovementPresets.getAll().forEach(([key, preset]) => {
       const btn = document.createElement('button');
       btn.className = 'preset-btn';
       btn.textContent = preset.name;
       btn.addEventListener('click', () => {
           Object.entries(preset.params).forEach(([param, value]) => {
               display.setGlobalSceneParameter(param, value);
               // Update UI sliders
               const slider = document.getElementById(`global-param-${param}`);
               if (slider) slider.value = value;
           });
       });
       presetContainer.appendChild(btn);
   });
   ```

3. **VolumetricDisplay.js**
   - Add `applyPreset(presetName)` method for batch parameter updates

**Testing:** Verify presets apply correct parameter combinations, UI updates properly

---

### ✅ Task 3.2: Improve Parameter Mapping Transparency

**Files to modify:**
- `src/js/main.js`
- `src/css/styles.css`

**Changes:**

1. **main.js - createGlobalSliderControl()**
   - Add info tooltip after parameter name showing scene-specific mapping:
   ```javascript
   const infoIcon = document.createElement('span');
   infoIcon.className = 'param-info-icon';
   infoIcon.textContent = 'ⓘ';
   infoIcon.title = getParameterMappingInfo(paramName, currentSceneType);
   labelEl.appendChild(infoIcon);
   ```

2. **main.js - Add getParameterMappingInfo() function**
   ```javascript
   function getParameterMappingInfo(paramName, sceneType) {
       const mappings = {
           size: {
               shapeMorph: 'Object radius',
               particleFlow: 'Particle size (1-5)',
               procedural: 'Noise scale (inverse)',
               plasma: 'Wave scale (inverse)'
           },
           amplitude: {
               waveField: 'Wave height (0.5-3.0)',
               procedural: 'Density threshold (inverse)',
               vortex: 'Vortex radius'
           }
           // ... etc
       };
       return mappings[paramName]?.[sceneType] || 'Affects this scene';
   }
   ```

3. **main.js - updateActiveGlobalIndicators()**
   - Add badge showing non-default values:
   ```javascript
   if (activeParams.includes(paramName)) {
       el.classList.add('active');
       const currentVal = display.getGlobalSceneParameter(paramName);
       const defaultVal = GlobalParameterMapper.getDefaults()[paramName];
       if (currentVal !== defaultVal) {
           el.classList.add('modified');
       }
   }
   ```

4. **styles.css**
   ```css
   .global-param.modified {
       border-left: 3px solid #ffa500;
   }
   .param-info-icon {
       margin-left: 5px;
       cursor: help;
       opacity: 0.6;
   }
   ```

**Testing:** Verify tooltips show correct mappings, modified parameters highlighted

---

### ✅ Task 3.3: Add Automation Presets UI

**Files to create:**
- `src/js/utils/AutomationPresets.js` (NEW)

**Files to modify:**
- `src/js/main.js` (automation modal)

**Changes:**

1. **Create AutomationPresets.js**
   ```javascript
   export class AutomationPresets {
       static presets = {
           'gentleSway': {
               name: 'Gentle Sway',
               config: { waveType: 'sine', frequency: 0.3, amplitude: 0.3, phase: 0 }
           },
           'rhythmicPulse': {
               name: 'Rhythmic Pulse',
               config: { waveType: 'square', frequency: 1.0, amplitude: 0.5, phase: 0 }
           },
           'randomDrift': {
               name: 'Random Drift',
               config: { waveType: 'sine', frequency: 0.15, amplitude: 0.6, phase: Math.random() * Math.PI * 2 }
           },
           'breathing': {
               name: 'Breathing',
               config: { waveType: 'sine', frequency: 0.5, amplitude: 0.4, phase: 0 }
           },
           'erratic': {
               name: 'Erratic',
               config: { waveType: 'triangle', frequency: 2.0, amplitude: 0.8, phase: 0 }
           }
       };

       static getPreset(name) { return this.presets[name]; }
       static getAll() { return Object.entries(this.presets); }
   }
   ```

2. **main.js - Update automation modal** (~line 1018)
   - Add preset selector before wave type dropdown:
   ```html
   <div class="control-group">
       <label>Preset</label>
       <select id="automation-preset">
           <option value="">Custom</option>
           <!-- AutomationPresets populated here -->
       </select>
   </div>
   ```
   - Add event listener to load preset values into modal inputs
   - Add "Apply to Multiple Parameters" checkbox + multi-select list

**Testing:** Verify presets load into modal, apply correctly, multi-apply works

---

### ✅ Task 3.4: Add Parameter Lock System

**Files to modify:**
- `src/js/main.js`
- `src/js/VolumetricDisplay.js`
- `src/css/styles.css`

**Changes:**

1. **VolumetricDisplay.js**
   - Add `lockedParameters` Set to track locked params
   - Add methods: `lockParameter(name)`, `unlockParameter(name)`, `isParameterLocked(name)`
   - Update `setScene()` to preserve locked parameter values when switching

2. **main.js - createGlobalSliderControl()**
   - Add lock button after value display:
   ```javascript
   const lockBtn = document.createElement('button');
   lockBtn.className = 'param-lock-btn';
   lockBtn.innerHTML = '🔓';
   lockBtn.addEventListener('click', () => {
       const locked = display.toggleParameterLock(paramName);
       lockBtn.innerHTML = locked ? '🔒' : '🔓';
       group.classList.toggle('locked', locked);
   });
   labelEl.appendChild(lockBtn);
   ```

3. **main.js - updateSceneControls()**
   - Check locked params before resetting values:
   ```javascript
   if (!display.isParameterLocked(paramName)) {
       slider.value = defaultValue;
   }
   ```

4. **styles.css**
   ```css
   .global-param.locked {
       background: rgba(255, 215, 0, 0.1);
       border-left: 3px solid gold;
   }
   .param-lock-btn {
       background: none;
       border: none;
       cursor: pointer;
       font-size: 14px;
       margin-left: 5px;
   }
   ```

5. **Add localStorage persistence**
   - Save locked params on lock/unlock
   - Load locked params on init

**Testing:** Verify parameters stay locked when switching scenes, persist across sessions

---

## 📊 Progress Tracking

| Phase | Task | Status | Files Modified | Lines Changed | Priority |
|-------|------|--------|----------------|---------------|----------|
| 1 | 1.1 translateY | ✅ Completed | 3 | ~30 | HIGH |
| 1 | 1.2 Movement All Scenes | ⬜ Not Started | 2 | ~200 | HIGH |
| 1 | 1.3 UI Grouping | ✅ Completed | 2 | ~150 | MEDIUM |
| 2 | 2.1 Merge Illusions | ⬜ Not Started | 4 | ~50 | MEDIUM |
| 2 | 2.2 Merge Plasma | ⬜ Not Started | 2 | ~80 | MEDIUM |
| 3 | 3.1 Movement Presets | ⬜ Not Started | 3 | ~150 | MEDIUM |
| 3 | 3.2 Mapping Transparency | ⬜ Not Started | 2 | ~80 | LOW |
| 3 | 3.3 Automation Presets | ⬜ Not Started | 2 | ~120 | LOW |
| 3 | 3.4 Parameter Locks | ⬜ Not Started | 3 | ~150 | MEDIUM |

**Total Estimated Changes:** ~960 lines across 8-10 files

---

## 🎯 Recommended Execution Order

1. ✅ Task 1.1 (translateY) - Quick win, isolated
2. ✅ Task 1.3 (UI Grouping) - Improves UX immediately
3. ✅ Task 3.1 (Movement Presets) - Uses existing controls
4. ✅ Task 2.2 (Merge Plasma) - Simplifies architecture
5. ✅ Task 2.1 (Merge Illusions) - Major refactor
6. ✅ Task 1.2 (Movement All Scenes) - Complex, depends on architecture
7. ✅ Task 3.3 (Automation Presets) - Enhancement
8. ✅ Task 3.4 (Parameter Locks) - New infrastructure
9. ✅ Task 3.2 (Mapping Transparency) - Polish

---

## ⚠️ Testing Checklist (After Each Task)

- [ ] All scenes render without errors
- [ ] Parameter controls update scene correctly
- [ ] UI controls remain responsive
- [ ] No console errors
- [ ] Movement effects stack correctly
- [ ] Automation system still works
- [ ] Scene switching preserves expected state
- [ ] FPS remains acceptable (>30fps)

---

## 📝 Notes & Decisions

- **Decision Log:**
  - Keeping wobble separate rather than merging into rotation (user may want both)
  - Using category tags instead of separate libraries (simpler architecture)
  - localStorage for parameter locks (no backend needed)

- **Future Considerations (Phase 4+):**
  - Visual path designer
  - Effect chaining UI
  - Scene blending/compositing
  - Preset save/load to JSON
  - Timeline/keyframe system

---

## 🔧 Rollback Plan

If any task breaks functionality:
1. Git revert to commit before task
2. Document issue in this file
3. Skip task and continue with others
4. Revisit problematic task after other tasks complete

---

**Last Updated:** 2025-10-17
**Next Review:** After Phase 1 completion
