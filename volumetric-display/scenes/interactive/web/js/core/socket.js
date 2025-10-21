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
