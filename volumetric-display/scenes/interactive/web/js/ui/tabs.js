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

// Update which tabs are enabled/disabled based on scene
export function updateTabStates(sceneType, sceneConfig) {
    const config = sceneConfig[sceneType];
    if (!config) return;

    const allTabs = ['scale', 'rotation', 'translation', 'scrolling', 'copy', 'particles'];
    const enabledTabs = config.enabledTabs || [];

    // Special handling: hide PART for non-physics, hide COP for physics
    const isPhysics = sceneType === 'physics';

    allTabs.forEach(tabName => {
        const tabBtn = document.querySelector(`.subtab-btn[data-subtab="${tabName}"]`);
        if (!tabBtn) return;

        // Special visibility rules for particles and copy tabs
        if (tabName === 'particles') {
            // Only show particles tab for physics scenes
            if (isPhysics) {
                tabBtn.style.display = '';
            } else {
                tabBtn.style.display = 'none';
                return;
            }
        } else if (tabName === 'copy') {
            // Only show copy tab for non-physics scenes
            if (!isPhysics) {
                tabBtn.style.display = '';
            } else {
                tabBtn.style.display = 'none';
                return;
            }
        } else {
            // All other tabs are always visible
            tabBtn.style.display = '';
        }

        // Enable/disable based on scene config
        if (enabledTabs.includes(tabName)) {
            // Enable tab
            tabBtn.classList.remove('disabled');
            tabBtn.removeAttribute('title');
        } else {
            // Disable tab with tooltip
            tabBtn.classList.add('disabled');
            tabBtn.setAttribute('title', `Not available for ${sceneType}`);
        }
    });
}

// Switch to a valid tab if current tab is not available for new scene
export function switchToValidTab(sceneType, sceneConfig) {
    const config = sceneConfig[sceneType];
    if (!config) return;

    const enabledTabs = config.enabledTabs || [];

    // Find currently active tab
    const activeTabBtn = document.querySelector('.subtab-btn.active');
    const currentTab = activeTabBtn?.dataset.subtab;

    // If current tab is valid for new scene, keep it
    if (currentTab && enabledTabs.includes(currentTab)) {
        return;
    }

    // Otherwise, switch to first available tab
    if (enabledTabs.length > 0) {
        switchSubtab(enabledTabs[0]);
    }
}
