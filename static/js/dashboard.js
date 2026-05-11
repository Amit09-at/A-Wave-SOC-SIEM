let trafficChart;
let map;

document.addEventListener('DOMContentLoaded', () => {
    startClock();
    initMap();
    initChart();

    // Start Polling
    refreshData();
    setInterval(refreshData, 3000);
});

// --- UI UTILS ---
function startClock() {
    setInterval(() => {
        document.getElementById('clock').innerText = new Date().toLocaleTimeString('en-US', { hour12: false });
    }, 1000);
}

function toggleProfile() {
    document.getElementById('profileDropdown').classList.toggle('show');
}

function logout() {
    fetch('/api/logout').then(() => window.location.href = '/login.html');
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// --- DATA LOGIC ---
async function refreshData() {
    try {
        const stats = await (await fetch("/api/stats")).json();
        document.getElementById("totalLogs").innerText = stats.total_logs;
        document.getElementById("totalAlerts").innerText = stats.total_alerts;

        const alerts = await (await fetch("/api/alerts")).json();
        updateTable(alerts);
        updateMap(alerts);
        updateTicker(alerts);
        checkHoneyfile(alerts);

        addDataToChart(Math.floor(Math.random() * 20) + 5);
    } catch (e) {
        console.error("Sync Error:", e);
    }
}

function updateTable(alerts) {
    const tbody = document.getElementById("alertsTable");
    tbody.innerHTML = "";

    alerts.slice(0, 15).forEach(alert => {
        const row = document.createElement("tr");
        row.setAttribute("data-search", `${alert.ip_address} ${alert.alert_type} ${alert.severity}`.toLowerCase());

        const sevColor = alert.severity === 'CRITICAL' || alert.severity === 'HIGH' ? '#ef4444' : '#f59e0b';
        const safeAlert = encodeURIComponent(JSON.stringify(alert));

        row.innerHTML = `
            <td>${alert.timestamp.split(' ')[1]}</td>
            <td style="font-family: monospace; color: #67e8f9;">${alert.ip_address}</td>
            <td>${alert.alert_type}</td>
            <td style="color:${sevColor}; font-weight:bold;">${alert.severity}</td>
            <td>
                <button class="btn-scan" onclick="viewCase('${safeAlert}')">Review</button>
                <button class="btn-scan" style="background:rgba(239,68,68,0.2); border-color:#ef4444; color:#ef4444;" onclick="runIPScan('${alert.ip_address}', this)">Scan</button>
                <button class="btn-scan" style="background: #007bff; color: white; border-color: #007bff;" onclick="askAIBot('${alert.ip_address}', '${alert.alert_type}')">🤖 Ask AI</button>
            </td>
        `;
        tbody.appendChild(row);
    });
    filterTable();
}

function filterTable() {
    const input = document.getElementById("searchInput").value.toLowerCase();
    const rows = document.getElementById("alertsTable").getElementsByTagName("tr");
    for (let i = 0; i < rows.length; i++) {
        const txt = rows[i].getAttribute("data-search");
        rows[i].style.display = (txt && txt.includes(input)) ? "" : "none";
    }
}

async function runIPScan(ip, btn) {
    btn.innerText = "Scanning...";
    btn.disabled = true;

    try {
        const res = await fetch('/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ip: ip })
        });
        const data = await res.json();
        alert(`SCAN REPORT FOR ${data.target}\n\nRISK SCORE: ${data.risk_score}/100\nPORTS: ${data.ports.join(', ')}\nVULNS: ${data.vulns.join(', ')}`);
        btn.innerText = "Scanned";
        btn.style.opacity = "0.5";
    } catch (e) {
        alert("Scan Failed: " + e);
        btn.innerText = "Retry";
        btn.disabled = false;
    }
}

function viewCase(alertData) {
    const a = JSON.parse(decodeURIComponent(alertData));
    const url = `/api/generate_report?type=${a.alert_type}&ip=${a.ip_address}&desc=${encodeURIComponent(a.description)}`;
    window.open(url, '_blank');
}

function downloadReport() {
    window.location.href = '/api/download_report';
}

function checkHoneyfile(alerts) {
    const triggered = alerts.some(a => a.alert_type.includes("Deception") || a.alert_type.includes("Honey"));
    const card = document.getElementById("honeyCard");
    const status = document.getElementById("honeyStatus");

    if (triggered) {
        card.classList.add("honey-active");
        status.innerText = "BREACH DETECTED";
        status.style.color = "#ffffff";
    } else {
        card.classList.remove("honey-active");
        status.innerText = "ARMED";
        status.style.color = "#10b981";
    }
}

function updateTicker(alerts) {
    const ticker = document.getElementById("logTicker");
    if (alerts.length > 0) {
        const latest = alerts[0];
        const line = document.createElement('div');
        line.innerText = `[${latest.timestamp.split(' ')[1]}] PACKET: SRC=${latest.ip_address} PROTO=TCP FLAG=${latest.severity}`;
        ticker.prepend(line);
        if (ticker.children.length > 8) ticker.lastChild.remove();
    }
}

// --- VISUALIZATION SETUP ---
function initMap() {
    if (map) return;
    map = L.map('map', { zoomControl: false, attributionControl: false }).setView([20.0, 0.0], 1);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { maxZoom: 19 }).addTo(map);
}

function updateMap(alerts) {
    if (!map) return;
    map.eachLayer(l => { if (l instanceof L.CircleMarker) map.removeLayer(l); });

    alerts.forEach(a => {
        const lat = (Math.random() * 120) - 60;
        const lng = (Math.random() * 360) - 180;
        const color = a.severity === 'CRITICAL' ? '#ef4444' : '#f59e0b';
        L.circleMarker([lat, lng], { color: color, radius: 4 }).addTo(map);
    });
}

function initChart() {
    const ctx = document.getElementById('trafficChart').getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(6, 182, 212, 0.5)');
    gradient.addColorStop(1, 'rgba(6, 182, 212, 0)');

    const labels = [];
    const now = new Date();
    for (let i = 9; i >= 0; i--) {
        const d = new Date(now.getTime() - i * 60000 * 10);
        const hours = String(d.getHours()).padStart(2, '0');
        const mins = String(d.getMinutes()).padStart(2, '0');
        labels.push(`${hours}:${mins}`);
    }

    trafficChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: Array(10).fill(0),
                borderColor: '#06b6d4',
                backgroundColor: gradient,
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } },
                y: { display: false }
            }
        }
    });
}

function addDataToChart(data) {
    trafficChart.data.datasets[0].data.shift();
    trafficChart.data.datasets[0].data.push(data);

    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const mins = String(now.getMinutes()).padStart(2, '0');
    trafficChart.data.labels.shift();
    trafficChart.data.labels.push(`${hours}:${mins}`);

    trafficChart.update('none');
}

// --- MODAL LOGIC (AI, LOGS, THREAT INTEL, SETTINGS) ---

function askAIBot(ip, alertType) {
    document.getElementById('ai-modal').style.display = 'block';
    document.getElementById('ai-content').innerHTML = '<p style="color: #007bff; font-weight: bold;">🤖 <em>AI Copilot is connecting to OSINT servers... please wait.</em></p>';

    fetch('/api/ai_assist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip: ip, alert_type: alertType })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                document.getElementById('ai-content').innerHTML = `
                <h4 style="color: #d32f2f; margin-top: 0;">🚨 OSINT Threat Analysis</h4>
                <p style="color: #333;">${data.ai_analysis}</p>
                <h4 style="color: #10b981; margin-top: 15px;">🛡️ Recommended Action</h4>
                <p style="color: #333;">${data.ai_recommendation}</p>
            `;
            }
        })
        .catch(err => {
            document.getElementById('ai-content').innerHTML = '<p>❌ Connection to AI Engine failed.</p>';
        });
}

function fetchLiveLogs() {
    document.getElementById('logs-modal').style.display = 'block';
    document.getElementById('raw-logs-content').innerText = "Establishing secure connection to core telemetry...\n";

    fetch('/api/logs/live')
        .then(response => response.json())
        .then(data => {
            document.getElementById('raw-logs-content').innerText = data.logs;
        })
        .catch(err => {
            document.getElementById('raw-logs-content').innerText = "FATAL: Could not connect to log server.";
        });
}

function openThreatModal() {
    document.getElementById('threat-modal').style.display = 'block';

    fetch('/api/threat_intel')
        .then(res => res.json())
        .then(data => {
            let html = "";
            data.feed.forEach(item => {
                let color = item.severity === 'CRITICAL' ? '#ef4444' : (item.severity === 'HIGH' ? '#f97316' : '#eab308');
                html += `
                <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid ${color};">
                    <div style="color: #94a3b8; font-size: 12px; margin-bottom: 5px;">[${item.date}] - Severity: <strong style="color:${color};">${item.severity}</strong></div>
                    <div style="color: white; font-size: 14px;">${item.threat}</div>
                </div>`;
            });
            document.getElementById('threat-content').innerHTML = html;
        });
}

function openSettingsModal() {
    document.getElementById('settings-modal').style.display = 'block';
    // Hide the dropdown menu when opening settings
    document.getElementById('profileDropdown').classList.remove('show');
}