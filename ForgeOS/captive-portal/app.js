// ForgeOS Dev Provisioner Logic
let currentStep = 1;
const totalSteps = 4;

const API_BASE_URLS = {
    groq: 'https://api.groq.com/openai/v1',
    cerebras: 'https://api.cerebras.ai/v1'
};

const state = {
    wifiSSID: 'UNESP-Academica',
    wifiPass: '',
    dhcp: true,
    apiProvider: 'groq',
    apiBaseUrl: 'https://api.groq.com/openai/v1',
    apiKey: '',
    windowMode: '-g right'
};

function updateStepUI() {
    document.querySelectorAll('.card-step').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.nav-step').forEach(n => n.classList.remove('active'));

    document.getElementById(`step-${currentStep}`).classList.add('active');
    document.querySelector(`.nav-step[data-step="${currentStep}"]`).classList.add('active');

    document.getElementById('step-num-display').innerText = currentStep;
    document.getElementById('btn-back').disabled = currentStep === 1;

    const btnNext = document.getElementById('btn-next');
    if (currentStep === totalSteps) {
        btnNext.style.display = 'none';
    } else {
        btnNext.style.display = 'inline-block';
    }

    updateSummary();
}

function nextStep() {
    if (currentStep < totalSteps) {
        currentStep++;
        updateStepUI();
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateStepUI();
    }
}

function selectWifi(ssid) {
    state.wifiSSID = ssid;
    document.getElementById('wifi-ssid').value = ssid;
    
    document.querySelectorAll('.wifi-option').forEach(opt => opt.classList.remove('selected'));
    event.currentTarget.classList.add('selected');
}

function updateApiBaseUrl() {
    const provider = document.getElementById('api-provider').value;
    state.apiProvider = provider;
    state.apiBaseUrl = API_BASE_URLS[provider] || API_BASE_URLS.groq;
    document.getElementById('api-base-url').value = state.apiBaseUrl;
}

function updateWindowMode(val) {
    state.windowMode = val;
    document.querySelectorAll('.radio-option').forEach(opt => {
        const radio = opt.querySelector('input[type="radio"]');
        if (radio && radio.value === val) {
            opt.classList.add('active');
            radio.checked = true;
        } else {
            opt.classList.remove('active');
        }
    });
}

function updateSummary() {
    document.getElementById('sum-wifi').innerText = `${state.wifiSSID} (${state.dhcp ? 'DHCP' : 'Static'})`;
    document.getElementById('sum-provider').innerText = `${state.apiProvider.toUpperCase()} (${state.apiBaseUrl})`;
    
    const keySet = state.apiKey.trim().length > 0;
    document.getElementById('sum-key').innerText = keySet ? 'Chave Configurada (••••••••)' : 'Não informada';
    document.getElementById('sum-window').innerText = state.windowMode;
}

function executeProvision() {
    const term = document.getElementById('terminal-log');
    term.innerHTML = '';

    function print(msg) {
        const p = document.createElement('p');
        p.className = 'log';
        p.innerText = msg;
        term.appendChild(p);
        term.scrollTop = term.scrollHeight;
    }

    print('[FORGEOS] Gravação em /boot/forge/...');
    setTimeout(() => print(`[NET] Configurado Wi-Fi SSID: ${state.wifiSSID}`), 400);
    setTimeout(() => print(`[MINA] Configurado Provedor: ${state.apiProvider} (${state.apiBaseUrl})`), 900);
    setTimeout(() => print(`[MINA] Argumento de Janela CLI: ${state.windowMode}`), 1400);
    setTimeout(() => print('[SYSTEMD] Habilitando mina-assistant.service... OK'), 1900);
    setTimeout(() => {
        print('[SUCCESS] Gravado /boot/forge/network.yaml e /boot/forge/mina.yaml');
        print('[REBOOT] Reiniciando TV Box...');

        fetch('/api/provision', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(state)
        }).catch(err => console.log('Simulação backend local:', err));
    }, 2400);
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('wifi-ssid').addEventListener('input', e => state.wifiSSID = e.target.value);
    document.getElementById('wifi-pass').addEventListener('input', e => state.wifiPass = e.target.value);
    document.getElementById('dhcp-check').addEventListener('change', e => state.dhcp = e.target.checked);

    document.getElementById('api-key').addEventListener('input', e => state.apiKey = e.target.value);

    document.querySelectorAll('.nav-step').forEach(nav => {
        nav.addEventListener('click', () => {
            currentStep = parseInt(nav.getAttribute('data-step'));
            updateStepUI();
        });
    });
});
