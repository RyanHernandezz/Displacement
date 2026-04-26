// Globals
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
const canvas = document.getElementById('sim-canvas');
const ctx = canvas.getContext('2d');
let particles = [];
let edges = [];
let aiWaveHistory = [];
let businessCycleHistory = [];
const maxWaveHistory = 150;



// Resize Canvas
function resizeCanvas() {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// Colors
const pathColors = {
    'Credentialed': '#64748b',
    'Corporate': '#ff003c',
    'Emerging': '#10b981',
    'Entrepreneur': '#f59e0b'
};

const archColors = {
    'SocialMirror': '#3b82f6',
    'NarrativeCaptive': '#a855f7',
    'AnchoredExtrapolator': '#f59e0b',
    'EmotionDriven': '#ef4444',
    'LossAversion': '#14b8a6',
    'ProbabilisticBayesian': '#10b981',
    'StrategicOptions': '#ec4899',
    'Credentialist': '#64748b'
};

// Charts Setup
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    elements: { point: { radius: 0 }, line: { borderWidth: 2 } },
    scales: {
        x: { display: false },
        y: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#888' } }
    },
    plugins: { legend: { labels: { color: '#f0f0f0' } } }
};






// Archetype Explorer State & Charts
let selectedArchetype = 'StrategicOptions';

const archSelectorDiv = document.getElementById('arch-selector');
Object.keys(archColors).forEach(arch => {
    const pill = document.createElement('div');
    pill.innerText = arch;
    pill.style.padding = '4px 8px';
    pill.style.borderRadius = '12px';
    pill.style.fontSize = '0.75em';
    pill.style.cursor = 'pointer';
    pill.style.border = `1px solid ${archColors[arch]}`;
    pill.style.color = archColors[arch];
    pill.onclick = () => { selectArchetype(arch); };
    pill.id = `pill-${arch}`;
    archSelectorDiv.appendChild(pill);
});

function selectArchetype(arch) {
    selectedArchetype = arch;
    // Update pill visuals
    Object.keys(archColors).forEach(k => {
        const p = document.getElementById(`pill-${k}`);
        if (k === arch) {
            p.style.backgroundColor = archColors[k];
            p.style.color = '#fff';
        } else {
            p.style.backgroundColor = 'transparent';
            p.style.color = archColors[k];
        }
    });
}


const archDistCtx = document.getElementById('arch-dist-chart').getContext('2d');
const archDistChart = new Chart(archDistCtx, {
    type: 'bar',
    data: {
        labels: [...Object.keys(pathColors), 'Unemployed'],
        datasets: [{
            label: 'Count',
            data: [0, 0, 0, 0, 0],
            backgroundColor: [...Object.values(pathColors), 'rgba(255,255,255,0.3)']
        }]
    },
    options: {
        ...chartOptions,
        plugins: { title: { display: true, text: 'Selected Arch Distribution', color: '#fff' }, legend: { display: false } },
        scales: { x: { display: true } }
    }
});

// Select default initially
selectArchetype(selectedArchetype);

// WebSocket Handling
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'projection_result') {
        document.getElementById('projection-loading').style.display = 'none';
        const tbody = document.querySelector('#projection-table tbody');
        tbody.innerHTML = '';
        
        let reportData = data.data;
        reportData.sort((a, b) => a.structural_unemp_rate - b.structural_unemp_rate);
        
        reportData.forEach(row => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid #333';
            tr.innerHTML = `
                <td style="padding:8px;">${row.archetype}</td>
                <td style="padding:8px;">${row.initial_path}</td>
                <td style="padding:8px;">${row.count}</td>
                <td style="padding:8px;">${row.avg_age.toFixed(1)}</td>
                <td style="padding:8px; color: #ef4444;">${(row.avg_unemployed_pct * 100).toFixed(1)}%</td>
                <td style="padding:8px;">${(row.structural_unemp_rate * 100).toFixed(1)}%</td>
            `;
            tbody.appendChild(tr);
        });
        document.getElementById('projection-table').style.display = 'table';
        return;
    }
    
    particles = data.particles;
    edges = data.edges;
    let tick = data.tick;
    
    // AI Wave Tracking
    const aiWave = data.ai_wave !== undefined ? data.ai_wave : 0;
    aiWaveHistory.push(aiWave);
    if (aiWaveHistory.length > maxWaveHistory) {
        aiWaveHistory.shift();
    }
    
    // Business Cycle Tracking
    const businessCycle = data.business_cycle !== undefined ? data.business_cycle : 0;
    businessCycleHistory.push(businessCycle);
    if (businessCycleHistory.length > maxWaveHistory) {
        businessCycleHistory.shift();
    }
    
    if (data.metrics && data.metrics.longitudinal_report) {
        renderReport(data.metrics.longitudinal_report);
    }
    
    
    // Update deep dive strictly for selected archetype
    const snap = data.metrics.archetype_snapshot[selectedArchetype];
    if (snap) {
        archDistChart.data.datasets[0].data = [
            snap.path_distribution['Credentialed'] || 0,
            snap.path_distribution['Corporate'] || 0,
            snap.path_distribution['Emerging'] || 0,
            snap.path_distribution['Entrepreneur'] || 0,
            snap.path_distribution['Unemployed'] || 0
        ];
        archDistChart.update();
        
        const summary = document.getElementById('arch-summary');
        const count = snap.count;
        const share = (snap.share_of_labor_market * 100).toFixed(1);
        const failRate = (snap.catastrophic_failure_rate * 100).toFixed(1);
        const emergingShare = (snap.active_in_emerging_fields * 100).toFixed(1);
        const reskillingRate = (snap.reskilling_rate * 100).toFixed(1);
        
        let desc = "";
        if (selectedArchetype === 'StrategicOptions') desc = "Highly adaptive. High risk tolerance and fast learning speed.";
        if (selectedArchetype === 'ProbabilisticBayesian') desc = "Data-driven. Updates rationally based on market signals.";
        if (selectedArchetype === 'SocialMirror') desc = "Network-driven. Herds with peers rather than market signals.";
        if (selectedArchetype === 'NarrativeCaptive') desc = "Emotionally attached to public narrative hype or panic.";
        if (selectedArchetype === 'Credentialist') desc = "Institutionally constrained. Averse to uncredentialed emerging fields.";
        if (selectedArchetype === 'AnchoredExtrapolator') desc = "Stuck in the past. Slowly updates beliefs, high lock-in.";
        if (selectedArchetype === 'EmotionDriven') desc = "Reacts sharply to wage drops but directionless in recovery.";
        if (selectedArchetype === 'LossAversion') desc = "Terrified of downside. Will stay in failing path rather than risk shift.";

        summary.innerHTML = `
            <strong>${selectedArchetype}</strong>: ${desc}<br><br>
            Currently, they make up <strong>${share}%</strong> of the total labor market.<br>
            - <strong>Failure Rate:</strong> ${failRate}% are currently unemployed.<br>
            - <strong>Frontier Activity:</strong> ${emergingShare}% have successfully migrated to Emerging/Entrepreneur fields.<br>
            - <strong>Adaptation Effort:</strong> ${reskillingRate}% are actively reskilling.<br>
        `;
    }
};

// Reset Simulation
document.getElementById('reset-btn').addEventListener('click', () => {
    ws.send(JSON.stringify({ 
        type: 'reset',
        num_agents: parseInt(document.getElementById('num-agents').value)
    }));
    
    // Reset sliders on the frontend just to reflect defaults
    sliderSimSpeed.value = 1.0;
    valSimSpeed.textContent = '1.0x';
});

// Controls
const sliderSimSpeed = document.getElementById('sim-speed');
const valSimSpeed = document.getElementById('sim-speed-val');

function sendControls() {
    const sim_speed = parseFloat(sliderSimSpeed.value);
    
    valSimSpeed.textContent = sim_speed.toFixed(1) + 'x';

    ws.send(JSON.stringify({
        type: 'controls',
        sim_speed: sim_speed,
        
        ablation_contagion: document.getElementById('ablation-contagion').checked,
        ablation_treadmill: document.getElementById('ablation-treadmill').checked,
        ablation_necessity_ent: document.getElementById('ablation-necessity-ent').checked,
        ablation_financial: document.getElementById('ablation-financial').checked,
        ablation_network: document.getElementById('ablation-network').checked,
        ablation_frictional: document.getElementById('ablation-frictional').checked,
        
        ablation_arch_social: document.getElementById('ablation-arch-social').checked,
        ablation_arch_narrative: document.getElementById('ablation-arch-narrative').checked,
        ablation_arch_strategic: document.getElementById('ablation-arch-strategic').checked,
        ablation_arch_credentialist: document.getElementById('ablation-arch-credentialist').checked,
        ablation_arch_emotion: document.getElementById('ablation-arch-emotion').checked,
        ablation_arch_anchored: document.getElementById('ablation-arch-anchored').checked,
        ablation_arch_loss: document.getElementById('ablation-arch-loss').checked
    }));
}

document.getElementById('num-agents').addEventListener('input', (e) => {
    document.getElementById('num-agents-val').textContent = e.target.value + ' Agents';
});

sliderSimSpeed.addEventListener('input', sendControls);

document.querySelectorAll('input[type="checkbox"][id^="ablation-"]').forEach(cb => {
    cb.addEventListener('change', sendControls);
});

const playPauseBtn = document.getElementById('play-pause-btn');
let isPaused = false;
playPauseBtn.addEventListener('click', () => {
    isPaused = !isPaused;
    if (isPaused) {
        playPauseBtn.textContent = 'Play';
        ws.send(JSON.stringify({ type: 'pause' }));
    } else {
        playPauseBtn.textContent = 'Pause';
        ws.send(JSON.stringify({ type: 'play' }));
    }
});



document.getElementById('run-projection-btn').addEventListener('click', () => {
    document.getElementById('projection-loading').style.display = 'block';
    document.getElementById('projection-table').style.display = 'none';
    ws.send(JSON.stringify({ 
        type: 'run_projection',
        num_agents: parseInt(document.getElementById('num-agents').value)
    }));
});

function renderReport(data) {
    const reportData = data.generational;
    const compData = data.node_composition;
    
    const tbody = document.querySelector('#report-table tbody');
    tbody.innerHTML = '';
    
    reportData.sort((a, b) => a.structural_unemp_rate - b.structural_unemp_rate);
    
    reportData.forEach(row => {
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid #333';
        tr.innerHTML = `
            <td style="padding:8px;">${row.archetype}</td>
            <td style="padding:8px;">${row.initial_path}</td>
            <td style="padding:8px;">${row.count}</td>
            <td style="padding:8px;">${row.avg_age.toFixed(1)}</td>
            <td style="padding:8px; color: #ef4444;">${(row.avg_unemployed_pct * 100).toFixed(1)}%</td>
            <td style="padding:8px;">${(row.structural_unemp_rate * 100).toFixed(1)}%</td>
        `;
        tbody.appendChild(tr);
    });
    
    const compTbody = document.querySelector('#comp-table tbody');
    compTbody.innerHTML = '';
    
    compData.sort((a, b) => a.current_node.localeCompare(b.current_node) || b.count - a.count);
    
    compData.forEach(row => {
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid #333';
        tr.innerHTML = `
            <td style="padding:8px;">${row.current_node}</td>
            <td style="padding:8px;">${row.initial_path}</td>
            <td style="padding:8px;">${row.count}</td>
        `;
        compTbody.appendChild(tr);
    });
}



// Render Loop
function render() {
    // Clear canvas
    ctx.fillStyle = 'rgba(10, 10, 12, 1.0)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    const scaleX = canvas.width / 1600;
    const scaleY = canvas.height / 800;

    // Draw Edges
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    ctx.globalAlpha = 0.15;
    
    // Map particles by ID to ensure accurate edge rendering
    const pMap = {};
    particles.forEach(p => pMap[p.id] = p);
    
    edges.forEach(edge => {
        const p1 = pMap[edge[0]];
        const p2 = pMap[edge[1]];
        if(p1 && p2) {
            ctx.beginPath();
            ctx.moveTo(p1.x * scaleX, p1.y * scaleY);
            ctx.lineTo(p2.x * scaleX, p2.y * scaleY);
            ctx.stroke();
        }
    });
    ctx.stroke();

    // Draw Node Labels & Title
    ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.font = 'bold 28px Inter';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('Job Types', 800 * scaleX, 50 * scaleY);
    
    ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.font = 'bold 40px Inter';
    ctx.fillText('Credentialed', 400 * scaleX, 200 * scaleY);
    ctx.fillText('Corporate', 1200 * scaleX, 200 * scaleY);
    ctx.fillText('Emerging Tech', 400 * scaleX, 600 * scaleY);
    ctx.fillText('Entrepreneur', 1200 * scaleX, 600 * scaleY);
    ctx.fillStyle = 'rgba(255, 100, 100, 0.2)';
    ctx.fillText('Unemployed / Disrupted', 800 * scaleX, 750 * scaleY);

    // Update and Draw Tethers (Illuminated Intent)
    particles.forEach(p => {
        const px = p.x * scaleX;
        const py = p.y * scaleY;
        
        let tx = 0, ty = 0;
        if (p.path === 'Credentialed') { tx = 400; ty = 200; }
        else if (p.path === 'Corporate') { tx = 1200; ty = 200; }
        else if (p.path === 'Emerging') { tx = 400; ty = 600; }
        else if (p.path === 'Entrepreneur') { tx = 1200; ty = 600; }
        else if (p.state === 'Unemployed') { tx = 800; ty = 750; }
        
        tx *= scaleX;
        ty *= scaleY;
        
        const dist = Math.hypot(px - tx, py - ty);

        // Draw tether ONLY if they are actively traveling (far from their node)
        // Set to 200 to ensure they have fully broken orbit before drawing the line to avoid flashing
        if (dist > 200 && p.state !== 'Unemployed') {
            ctx.beginPath();
            ctx.moveTo(px, py);
            ctx.lineTo(tx, ty);
            
            const gradient = ctx.createLinearGradient(px, py, tx, ty);
            gradient.addColorStop(0, p.color);
            gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
            
            ctx.strokeStyle = gradient;
            ctx.lineWidth = 1.5;
            ctx.stroke();
        }
    });

    // Draw Particles
    particles.forEach(p => {
        const px = p.x * scaleX;
        const py = p.y * scaleY;
        
        // Draw outer shell (empty boundary)
        ctx.beginPath();
        ctx.arc(px, py, 4, 0, Math.PI * 2);
        ctx.strokeStyle = p.state === 'Unemployed' ? 'rgba(255, 255, 255, 0.5)' : p.color;
        ctx.lineWidth = 1;
        ctx.stroke();
        
        // Draw inner fill proportional to skill
        let skillRatio = Math.max(0.0, Math.min(1.0, p.skill / 1.2)); // Normalizing to ~1.2 as full
        if (skillRatio > 0.05) {
            ctx.beginPath();
            ctx.arc(px, py, 4 * skillRatio, 0, Math.PI * 2);
            ctx.fillStyle = p.state === 'Unemployed' ? 'rgba(255, 255, 255, 0.5)' : p.color;
            ctx.fill();
        }
        
        // If actively reskilling on the job, draw a pulsing white sweat/aura
        if (p.is_reskilling) {
            ctx.beginPath();
            const pulse = 6 + Math.sin(Date.now() * 0.01 + p.id) * 3;
            ctx.arc(px, py, pulse, 0, Math.PI * 2);
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.lineWidth = 1;
            ctx.stroke();
        }
    });

    // Draw AI Shock Graph
    drawAIShockGraph(scaleX, scaleY);
    
    // Draw Business Cycle Graph
    drawBusinessCycleGraph(scaleX, scaleY);

    requestAnimationFrame(render);
}

function drawAIShockGraph(scaleX, scaleY) {
    if (aiWaveHistory.length === 0) return;
    
    const w = 200;
    const h = 60;
    const x = canvas.width - w - 20;
    const y = 20;
    
    // Background
    ctx.fillStyle = 'rgba(15, 23, 42, 0.7)';
    ctx.fillRect(x, y, w, h);
    ctx.strokeStyle = '#334155';
    ctx.strokeRect(x, y, w, h);
    
    // Title
    ctx.fillStyle = '#ef4444';
    ctx.font = '12px Inter';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText('AI Disruption Wave', x + 10, y + 8);
    
    // Draw the line
    ctx.beginPath();
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    
    const step = w / maxWaveHistory;
    
    // Maximum expected wave height for scaling (can adjust if it overflows)
    const maxVal = Math.max(1.0, ...aiWaveHistory) * 1.2; 
    
    for (let i = 0; i < aiWaveHistory.length; i++) {
        const val = aiWaveHistory[i];
        // Normalize
        const normY = val / maxVal;
        const px = x + i * step;
        const py = y + h - (normY * (h - 20)); // leave top 20px for text
        
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
    }
    ctx.stroke();
    
    // Fill under line
    ctx.lineTo(x + (aiWaveHistory.length - 1) * step, y + h);
    ctx.lineTo(x, y + h);
    ctx.fillStyle = 'rgba(239, 68, 68, 0.1)';
    ctx.fill();
}

function drawBusinessCycleGraph(scaleX, scaleY) {
    if (businessCycleHistory.length === 0) return;
    
    const w = 200;
    const h = 60;
    const x = canvas.width - w - 20;
    const y = 90; // Positioned below AI Disruption Wave graph
    
    // Background
    ctx.fillStyle = 'rgba(15, 23, 42, 0.7)';
    ctx.fillRect(x, y, w, h);
    ctx.strokeStyle = '#334155';
    ctx.strokeRect(x, y, w, h);
    
    // Title
    ctx.fillStyle = '#ffb300';
    ctx.font = '12px Inter';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText('Business Cycle', x + 10, y + 8);
    
    // Draw the line
    ctx.beginPath();
    ctx.strokeStyle = '#ffb300';
    ctx.lineWidth = 2;
    
    const step = w / maxWaveHistory;
    
    for (let i = 0; i < businessCycleHistory.length; i++) {
        const val = businessCycleHistory[i]; 
        const normY = (val + 0.15) / 0.30; 
        const px = x + i * step;
        const py = y + h - 5 - (normY * (h - 25)); 
        
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
    }
    ctx.stroke();
    
    // Fill under line
    ctx.lineTo(x + (businessCycleHistory.length - 1) * step, y + h);
    ctx.lineTo(x, y + h);
    ctx.fillStyle = 'rgba(255, 179, 0, 0.1)';
    ctx.fill();
}

render();
