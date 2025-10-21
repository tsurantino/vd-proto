/**
 * ArtNet Bridge WebSocket Client
 * Connects web UI to Python ArtNet bridge server
 */

export class ArtNetBridge {
    constructor(serverUrl = 'http://localhost:5000') {
        this.serverUrl = serverUrl;
        this.socket = null;
        this.connected = false;
        this.stats = { fps: 0, frame_time_ms: 0, active_leds: 0 };
        this.config = { gridX: 0, gridY: 0, gridZ: 0, cubes: 0 };

        // Callbacks
        this.onConnect = null;
        this.onDisconnect = null;
        this.onStats = null;
        this.onStatus = null;

        // Throttle state updates to avoid flooding
        this.updateQueue = {};
        this.updateTimer = null;
        this.updateInterval = 50; // ms - 20 updates/sec max
    }

    /**
     * Connect to ArtNet bridge server
     */
    async connect() {
        try {
            // First check if server is available
            const status = await this.checkServerStatus();
            if (!status.connected) {
                throw new Error('ArtNet bridge server not running');
            }

            // Load Socket.IO client library if not already loaded
            if (typeof io === 'undefined') {
                await this._loadSocketIO();
            }

            // Create socket connection
            this.socket = io(this.serverUrl, {
                transports: ['websocket', 'polling'],
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 5000,
                reconnectionAttempts: 10
            });

            // Set up event handlers
            this.socket.on('connect', () => {
                console.log('✅ Connected to ArtNet bridge');
                this.connected = true;
                if (this.onConnect) this.onConnect();
            });

            this.socket.on('disconnect', () => {
                console.log('❌ Disconnected from ArtNet bridge');
                this.connected = false;
                if (this.onDisconnect) this.onDisconnect();
            });

            this.socket.on('stats', (stats) => {
                this.stats = stats;
                if (this.onStats) this.onStats(stats);
            });

            this.socket.on('status', (status) => {
                if (this.onStatus) this.onStatus(status);
            });

            this.socket.on('state', (state) => {
                console.log('Received state from server:', state);
            });

            this.socket.on('connect_error', (error) => {
                console.error('Connection error:', error);
            });

            return true;
        } catch (error) {
            console.error('Failed to connect to ArtNet bridge:', error);
            return false;
        }
    }

    /**
     * Disconnect from server
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        this.connected = false;
    }

    /**
     * Check server status via HTTP
     */
    async checkServerStatus() {
        try {
            const response = await fetch(`${this.serverUrl}/api/status`);
            const data = await response.json();
            this.config = data.config;
            this.stats = data.stats;
            return data;
        } catch (error) {
            return { connected: false, error: error.message };
        }
    }

    /**
     * Send rendered pixel frame to bridge
     * @param {Uint8Array} pixelData - Flattened pixel array (width * height * length * 3)
     * @param {number} width - Grid width
     * @param {number} height - Grid height
     * @param {number} length - Grid length/depth
     */
    sendFrame(pixelData, width, height, length) {
        if (!this.connected || !this.socket) {
            console.warn('ArtNet bridge not connected, skipping frame');
            return;
        }

        try {
            // Convert Uint8Array to base64 for efficient transfer
            const base64 = this._arrayBufferToBase64(pixelData);

            this.socket.emit('frame', {
                pixels: base64,
                width: width,
                height: height,
                length: length
            });
        } catch (error) {
            console.error('Error sending frame:', error);
        }
    }

    /**
     * Convert ArrayBuffer/Uint8Array to base64
     */
    _arrayBufferToBase64(buffer) {
        let binary = '';
        const bytes = new Uint8Array(buffer);
        const len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary);
    }

    /**
     * Load Socket.IO client library dynamically
     */
    async _loadSocketIO() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.socket.io/4.5.4/socket.io.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    /**
     * Get connection status
     */
    isConnected() {
        return this.connected;
    }

    /**
     * Get latest stats
     */
    getStats() {
        return this.stats;
    }

    /**
     * Get config info
     */
    getConfig() {
        return this.config;
    }
}
