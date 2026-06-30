/**
 * PulseCheck Neo // Advanced UI System Interactions Pipeline
 * Integrates Apple-style minimalism with PS5 fluid workspace transitions
 */

// 1. Live Command Terminal Subsystem Engine
function submitTerminalCommand() {
    const input = document.getElementById('terminal-input');
    if (!input) return;
    
    const cmd = input.value.trim();
    if (!cmd) return;
    
    // Echo command back to the stream view matrix
    logConsoleEvent(`[USER CMD]: ${cmd}`);
    
    // Process local structural macro instructions
    const normalCmd = cmd.toLowerCase();
    if (normalCmd === 'clear') {
        const stream = document.getElementById('terminal-stream-log');
        if (stream) stream.innerHTML = '';
    } else if (normalCmd === 'help') {
        logConsoleEvent('System tools: help, clear, optimize, baseline, telemetry');
    } else if (normalCmd === 'optimize') {
        logConsoleEvent('[CORE ENGINE]: Tuning hyperparameter weights across array cells...');
        setTimeout(() => { 
            logConsoleEvent('[CORE ENGINE]: Optimizations bound. Spatial variance optimized.'); 
            triggerAppleNotification("Hyperparameters successfully tuned.");
        }, 800);
    } else if (normalCmd === 'baseline') {
        injectDashboardScenario(0, 0);
        logConsoleEvent('[CORE ENGINE]: Matrix re-pinned to initial baseline vectors.');
    } else if (normalCmd === 'telemetry') {
        const cost = (Math.random() * 0.4 + 0.8).toFixed(2);
        logConsoleEvent(`[METRIC REPORT]: Engine processing cost: ${cost}ms @ 60Hz topology.`);
    } else {
        logConsoleEvent(`Command trace absent from path array: "${cmd}". Type "help".`);
    }
    
    input.value = '';
}

// 2. Automated Event Log Stream Interface Formatter
function logConsoleEvent(msg) {
    const log = document.getElementById('terminal-stream-log');
    if (!log) return;
    
    const now = new Date();
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
    
    const div = document.createElement('div');
    div.className = "animate-fade-in text-slate-300";
    div.innerHTML = `<span class="text-slate-500 font-mono">[${timeStr} SYS]:</span> ${msg}`;
    
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
}

// 3. Quick-Inject Volatility Sandbox Scenarios Controller
function injectDashboardScenario(materials, retention) {
    const sliderMat = document.getElementById('slider-materials');
    const sliderRet = document.getElementById('slider-retention');
    const lblMat = document.getElementById('lbl-shock-materials');
    const lblRet = document.getElementById('lbl-shock-retention');

    if (sliderMat && lblMat) {
        sliderMat.value = materials;
        lblMat.innerText = `+${materials}%`;
    }
    if (sliderRet && lblRet) {
        sliderRet.value = retention;
        lblRet.innerText = `-${retention}%`;
    }

    // Fire notice and pipe updates directly to your data handlers
    triggerAppleNotification(`Injected scenario profile: Cost +${materials}% / Retention -${retention}%`);
    logConsoleEvent(`Scenario injection frame vector modified to: [M: +${materials}%, R: -${retention}%]`);

    // Triggers your pre-existing data emit structure if it is present in your dashboard environment
    if (typeof dispatchDataPayloadStream === "function") {
        dispatchDataPayloadStream();
    } else if (typeof updateDashboardValues === "function") {
        updateDashboardValues();
    }
}

// 4. Hook up Terminal Input Key Listeners (Carries Enter Key Submission)
document.addEventListener('DOMContentLoaded', () => {
    const terminalInput = document.getElementById('terminal-input');
    if (terminalInput) {
        terminalInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                submitTerminalCommand();
            }
        });
    }
});