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
        sessionMemory.saveParam(sceneType, param, value);

        socketManager.sendParams(paramsManager.params);
    });
}

// Special handler for scrolling thickness (displays as percentage)
export function setupScrollingThickness(paramsManager, socketManager) {
    const scrollingSlider = document.getElementById('scrolling_thickness');
    const scrollingValueDisplay = document.getElementById('scrolling_thickness-value');

    if (!scrollingSlider || !scrollingValueDisplay) {
        console.warn('Scrolling thickness slider not found');
        return;
    }

    scrollingSlider.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        scrollingValueDisplay.textContent = value + '%';
        paramsManager.params.scrolling_thickness = value;
        paramsManager.params.scrolling_enabled = value > 0;
        socketManager.sendParams(paramsManager.params);
    });
}

// Update copy section visibility based on object count
export function updateCopySectionVisibility() {
    const copyCount = parseInt(document.getElementById('objectCount').value);
    const variationSection = document.getElementById('copy-variation-section');
    const spacingControl = document.getElementById('copy-spacing-control');
    const arrangementControl = document.getElementById('copy-arrangement-control');

    // Always show arrangement control
    arrangementControl.style.display = 'block';

    // Enable/disable sections based on copy count
    if (copyCount > 1) {
        variationSection.style.display = 'block';
        spacingControl.style.display = 'flex';
        // Remove disabled class and re-enable controls
        variationSection.querySelectorAll('.control-group').forEach(el => {
            el.classList.remove('slider-disabled');
            const slider = el.querySelector('input[type="range"]');
            if (slider) slider.disabled = false;
        });
        spacingControl.classList.remove('slider-disabled');
        const spacingSlider = spacingControl.querySelector('input[type="range"]');
        if (spacingSlider) spacingSlider.disabled = false;
        arrangementControl.classList.remove('slider-disabled');
    } else {
        variationSection.style.display = 'block';
        spacingControl.style.display = 'flex';
        // Add disabled class and disable controls
        variationSection.querySelectorAll('.control-group').forEach(el => {
            el.classList.add('slider-disabled');
            const slider = el.querySelector('input[type="range"]');
            if (slider) slider.disabled = true;
        });
        spacingControl.classList.add('slider-disabled');
        const spacingSlider = spacingControl.querySelector('input[type="range"]');
        if (spacingSlider) spacingSlider.disabled = true;
        arrangementControl.classList.add('slider-disabled');
    }
}
