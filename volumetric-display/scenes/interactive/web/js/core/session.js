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

    saveParam(sceneType, paramName, value) {
        if (!this.memory[sceneType]) {
            this.memory[sceneType] = {};
        }
        this.memory[sceneType][paramName] = value;
    }
}
