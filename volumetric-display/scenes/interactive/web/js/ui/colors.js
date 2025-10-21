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

export function setupColorEffectButtons(paramsManager, socketManager) {
    document.querySelectorAll('button[data-effect]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('button[data-effect]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            paramsManager.params.color_effect = btn.dataset.effect;
            socketManager.sendParams(paramsManager.params);
        });
    });
}
