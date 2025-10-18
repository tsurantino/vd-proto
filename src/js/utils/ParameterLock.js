/**
 * Parameter Lock System
 * Allows locking parameters so they persist across scene changes
 */

export class ParameterLock {
    constructor() {
        this.lockedParams = new Map();
        this.loadFromStorage();
    }

    /**
     * Lock a parameter with its current value
     * @param {string} paramId - Parameter ID (e.g., 'global-param-size')
     * @param {any} value - Current value to lock
     */
    lock(paramId, value) {
        this.lockedParams.set(paramId, value);
        this.saveToStorage();
    }

    /**
     * Unlock a parameter
     * @param {string} paramId - Parameter ID
     */
    unlock(paramId) {
        this.lockedParams.delete(paramId);
        this.saveToStorage();
    }

    /**
     * Check if a parameter is locked
     * @param {string} paramId - Parameter ID
     * @returns {boolean}
     */
    isLocked(paramId) {
        return this.lockedParams.has(paramId);
    }

    /**
     * Get locked value for a parameter
     * @param {string} paramId - Parameter ID
     * @returns {any|null}
     */
    getLockedValue(paramId) {
        return this.lockedParams.get(paramId) || null;
    }

    /**
     * Get all locked parameters
     * @returns {Map}
     */
    getAllLocked() {
        return new Map(this.lockedParams);
    }

    /**
     * Clear all locks
     */
    clearAll() {
        this.lockedParams.clear();
        this.saveToStorage();
    }

    /**
     * Save locked parameters to localStorage
     */
    saveToStorage() {
        try {
            const data = Array.from(this.lockedParams.entries());
            localStorage.setItem('vd-locked-params', JSON.stringify(data));
        } catch (e) {
            console.warn('Failed to save locked parameters to localStorage:', e);
        }
    }

    /**
     * Load locked parameters from localStorage
     */
    loadFromStorage() {
        try {
            const data = localStorage.getItem('vd-locked-params');
            if (data) {
                const entries = JSON.parse(data);
                this.lockedParams = new Map(entries);
            }
        } catch (e) {
            console.warn('Failed to load locked parameters from localStorage:', e);
            this.lockedParams = new Map();
        }
    }

    /**
     * Apply all locked parameters to the display
     * @param {object} display - VolumetricDisplay instance
     */
    applyLocks(display) {
        for (const [paramId, value] of this.lockedParams.entries()) {
            // Extract parameter name from ID
            const paramName = paramId.replace('global-param-', '').replace('scene-param-', '');

            // Determine if it's a global or scene parameter
            if (paramId.startsWith('global-param-')) {
                display.setGlobalSceneParameter(paramName, value);
            } else if (paramId.startsWith('scene-param-')) {
                display.setSceneParameter(paramName, value);
            }
        }
    }
}
