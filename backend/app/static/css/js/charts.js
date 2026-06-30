/**
 * PulseCheck Neo // Cinematic Charting Engine Pipeline
 * Handles Apple-style minimalist line-graph plotting & live parameter recalculations
 */

let runwayChartInstance = null;

// Initialize the Master Timeline Forecast Chart
document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('runwayTimelineChart');
    if (!ctx) return;

    // Generate gradient masks for an authentic, premium glowing data layer
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(34, 211, 238, 0.25)'); // Cyan Glow Edge
    gradient.addColorStop(1, 'rgba(34, 211, 238, 0.00)');

    const config = {
        type: 'line',
        data: {
            labels: ['Current', 'Month 3', 'Month 6', 'Month 9', 'Month 12', 'Month 15', 'Month 18'],
            datasets: [{
                label: 'Simulated Cash Runway Horizon',
                data: [35000, 34200, 35100, 37000, 39500, 42000, 46000], // Default mock baseline arrays
                borderColor: '#22d3ee',
                borderWidth: 2,
                pointBackgroundColor: '#22d3ee',
                pointBorderColor: 'rgba(255,255,255,0.1)',
                pointHoverRadius: 6,
                tension: 0.4, // Delivers smooth curved transitions rather than rigid steps
                fill: true,
                backgroundColor: gradient
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }, // Minimalist design skips cluttered legends
                tooltip: {
                    backgroundColor: 'rgba(10, 10, 20, 0.85)',
                    titleFont: { family: 'JetBrains Mono', size: 10 },
                    bodyFont: { family: 'Inter', size: 11 },
                    borderWidth: 1,
                    borderColor: 'rgba(255,255,255,0.08)',
                    displayColors: false,
                    padding: 10
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.01)', borderDash: [4, 4] },
                    ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 9 } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)', borderDash: [4, 4] },
                    ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 9 } }
                }
            }
        }
    };

    runwayChartInstance = new Chart(ctx, config);
    
    // Setup reactive listeners on the live volatility sliders
    setupSliderListeners();
});

// Watch input adjustments to recalculate values on the fly
function setupSliderListeners() {
    const materialsSlider = document.getElementById('slider-materials');
    const retentionSlider = document.getElementById('slider-retention');

    if (materialsSlider) {
        materialsSlider.addEventListener('input', (e) => {
            const val = e.target.value;
            document.getElementById('lbl-shock-materials').innerText = `+${val}%`;
            recomputeChartDataMatrix();
        });
    }

    if (retentionSlider) {
        retentionSlider.addEventListener('input', (e) => {
            const val = e.target.value;
            document.getElementById('lbl-shock-retention').innerText = `-${val}%`;
            recomputeChartDataMatrix();
        });
    }
}

// Recalculates visual trends based on slider input variables
function recomputeChartDataMatrix() {
    if (!runwayChartInstance) return;

    // Pull operational baseline structures safely out of hidden input fields
    const revenue = parseFloat(document.getElementById('field-revenue')?.value || 18000);
    const expenses = parseFloat(document.getElementById('field-expenses')?.value || 21000);
    const baseCash = parseFloat(document.getElementById('field-cash')?.value || 35000);
    
    // Pull active dynamic shock scalars
    const matShock = parseFloat(document.getElementById('slider-materials')?.value || 0) / 100;
    const retShock = parseFloat(document.getElementById('slider-retention')?.value || 0) / 100;

    // Apply adjustments directly across individual data nodes
    let computedCash = baseCash;
    let newTrendPoints = [baseCash];

    const adjustedMonthlyRevenue = revenue * (1 - retShock);
    const adjustedMonthlyExpenses = expenses * (1 + matShock);
    const netBurnRate = adjustedMonthlyRevenue - adjustedMonthlyExpenses;

    for (let i = 1; i <= 6; i++) {
        // Compound changes forward across a rolling 18-month simulation window (grouped by 3-month blocks)
        computedCash += (netBurnRate * 3);
        newTrendPoints.push(Math.max(0, Math.round(computedCash))); // Keep values non-negative
    }

    // Refresh chart datasets with smooth ease animations
    runwayChartInstance.data.datasets[0].data = newTrendPoints;
    runwayChartInstance.update();

    // Push calculation metrics up to the display nodes automatically
    updateWorkspaceNodes(adjustedMonthlyRevenue, adjustedMonthlyExpenses, netBurnRate);
}

// Push local data modifications directly down into the interlocking hex matrix layout
function updateWorkspaceNodes(rev, exp, net) {
    const revEl = document.getElementById('hex-val-revenue');
    const expEl = document.getElementById('hex-val-expenses');
    const runEl = document.getElementById('hex-val-runway');
    const riskEl = document.getElementById('hex-val-risk');

    if (revEl) revEl.innerText = `$${Math.round(rev).toLocaleString()}`;
    if (expEl) expEl.innerText = `$${Math.round(exp).toLocaleString()}`;
    
    if (runEl) {
        if (net >= 0) {
            runEl.innerText = 'Infinite';
            runEl.className = "text-xs font-semibold font-mono text-emerald-400 mt-1.5";
        } else {
            const baseCash = parseFloat(document.getElementById('field-cash')?.value || 35000);
            const monthsLeft = Math.abs(baseCash / net);
            runEl.innerText = `${monthsLeft.toFixed(1)} Mos`;
            runEl.className = "text-xs font-semibold font-mono text-rose-400 mt-1.5";
        }
    }

    if (riskEl) {
        let score = 0;
        if (net < 0) score += 35;
        if (Math.abs(net) > 5000) score += 40;
        document.getElementById('hex-val-risk').innerText = `${score}%`;
    }
}