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

// Global effect buttons (strobe, pulse)
export function setupEffectButtons(paramsManager, socketManager) {
    document.querySelectorAll('.effect-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const param = btn.dataset.param;
            const value = btn.dataset.value;

            // Remove active from current param buttons
            document.querySelectorAll(`.effect-btn[data-param="${param}"]`)
                .forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            paramsManager.params[param] = value;

            // If activating strobe (not off), deactivate pulse
            if (param === 'strobe' && value !== 'off') {
                paramsManager.params.pulse = 'off';
                document.querySelectorAll('.effect-btn[data-param="pulse"]')
                    .forEach(b => b.classList.remove('active'));
                document.querySelector('.effect-btn[data-param="pulse"][data-value="off"]')
                    .classList.add('active');
            }

            // If activating pulse (not off), deactivate strobe
            if (param === 'pulse' && value !== 'off') {
                paramsManager.params.strobe = 'off';
                document.querySelectorAll('.effect-btn[data-param="strobe"]')
                    .forEach(b => b.classList.remove('active'));
                document.querySelector('.effect-btn[data-param="strobe"][data-value="off"]')
                    .classList.add('active');
            }

            socketManager.sendParams(paramsManager.params);
        });
    });
}
