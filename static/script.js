// --- NAVIGATION & UI LOGIC ---
function switchTab(tabName) {
    // Hide all views
    document.querySelectorAll('.section-view').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

    // Show selected
    document.getElementById(`view-${tabName}`).classList.add('active');

    // Update Sidebar
    const navIndex = ['predict', 'history', 'analysis'].indexOf(tabName);
    if (navIndex >= 0) {
        document.querySelectorAll('.nav-item')[navIndex].classList.add('active');
    }
}

// --- CORE PREDICTION LOGIC ---
document.getElementById('pcosForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const btn = this.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = 'Analyzing... <i class="fas fa-spinner fa-spin"></i>';
    btn.disabled = true;

    const formData = new FormData(this);
    const data = {};

    // Fields that MUST remain strings (Pydantic Strictness)
    const stringFields = ['Menstrual_Cycle', 'Diet_Type', 'Smoking_Status', 'Veg_or_NonVeg'];

    for (let [key, value] of formData.entries()) {
        if (stringFields.includes(key)) {
            data[key] = value.toString();
        } else if (!isNaN(value) && value !== '') {
            data[key] = parseFloat(value);
        } else {
            data[key] = value;
        }
    }

    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };

    try {
        // 1. Predict
        const response = await fetch('/api/v1/predict', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            const detail = errorData.detail
                ? (typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail, null, 2))
                : "Unknown Server Error (No Detail)";
            throw new Error(`VALIDATION FAILED:\n${detail}`);
        }
        const result = await response.json();

        // 2. Explain (Async)
        fetchExplanation(data);

        showResult(result);

        // Save data for other tabs to use
        window.lastInputData = data;

    } catch (error) {
        alert("Error: " + error.message);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
});

async function fetchExplanation(inputData) {
    // Show loading state
    document.getElementById('explanation-section').innerHTML = '<p>Generating AI Explanation...</p>';

    const token = localStorage.getItem('token');
    try {
        const response = await fetch('/api/v1/explain/local', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(inputData)
        });
        if (response.ok) {
            const exp = await response.json();
            renderExplanation(exp);
        }
    } catch (e) { console.error(e); }
}

function renderExplanation(data) {
    let html = '<h4>💡 Why this result?</h4><ul style="list-style:none; padding:0;">';
    data.key_drivers.forEach(d => {
        const color = d.direction === 'RISK_INCREASING' ? '#d9534f' : '#198754';
        const icon = d.direction === 'RISK_INCREASING' ? '🔺' : '✅';
        html += `<li style="margin:8px 0; border-bottom:1px solid #eee; padding-bottom:5px;">
            <span style="font-weight:bold; color:${color}">${icon} ${d.feature}</span> 
            has a ${(d.impact_score * 100).toFixed(1)}% influence
        </li>`;
    });
    html += '</ul>';
    document.getElementById('explanation-section').innerHTML = html;
}

function showResult(data) {
    const modal = document.getElementById('resultModal');
    const bg = modal.querySelector('.modal-content');
    const title = modal.querySelector('.result-title');
    const icon = modal.querySelector('.result-icon');

    // Reset Style
    bg.className = 'modal-content';

    if (data.risk_class === 'high') {
        title.innerText = "High Probability Detected";
        title.style.color = '#dc3545';
        icon.innerText = "⚠️";
    } else {
        title.innerText = "Low Probability";
        title.style.color = '#198754';
        icon.innerText = "✅";
    }

    modal.querySelector('.result-prob').innerText = `Risk Score: ${data.probability}%`;

    // Add Chart Here
    setTimeout(() => renderRiskChart(data), 200);

    modal.classList.add('active');
}

function closeModal() {
    document.getElementById('resultModal').classList.remove('active');
}

// --- POPULATION ANALYSIS (ProtoDash) ---
async function runPopulationAnalysis() {
    const container = document.getElementById('protodash-results');
    container.innerHTML = '<p style="text-align:center">Finding similar patients...</p>';

    // Use last input or mock
    const data = window.lastInputData || { Age: 25, Weight_kg: 60 };

    const token = localStorage.getItem('token');
    try {
        const response = await fetch('/api/v1/analysis/prototypes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        const res = await response.json();
        container.innerHTML = '';

        if (res.prototypes) {
            res.prototypes.forEach(p => {
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0;">Similiarity: ${p.similarity_score}%</h4>
                        <span style="background:${p.profile.Risk === 'High' ? '#fee2e2' : '#d1fae5'}; color:${p.profile.Risk === 'High' ? '#b91c1c' : '#065f46'}; padding:4px 8px; border-radius:4px; font-size:0.8em;">${p.profile.Risk || 'Unknown'}</span>
                    </div>
                    <hr style="border:0; border-top:1px solid #eee; margin:10px 0;">
                    <p><strong>Age:</strong> ${p.profile.Age}</p>
                    <p><strong>Weight:</strong> ${p.profile.Weight}kg</p>
                    <p style="font-size:0.8rem; color:#666; margin-top:5px;">
                        Patient ID: Anon-${Math.floor(Math.random() * 1000)}
                    </p>
                `;
                container.appendChild(card);
            });
        }
    } catch (e) {
        container.innerHTML = '<p style="color:red">Analysis failed. Run a prediction first.</p>';
    }
}

// --- HISTORY LOGIC ---
async function loadHistory() {
    const container = document.getElementById('history-content');
    container.innerHTML = '<div class="timeline-item"><p>Fetching records...</p></div>';

    // Simulate API call for "anonymous"
    try {
        const response = await fetch('/api/v1/reports/history/anonymous');
        const res = await response.json();

        container.innerHTML = '';
        if (res.changes && res.changes.length > 0) {
            res.changes.forEach(c => {
                const item = document.createElement('div');
                item.className = 'timeline-item';
                item.innerHTML = `
                    <div class="timeline-dot"></div>
                    <strong>${c.feature}</strong>
                    <p>${c.description}</p>
                    <small style="color:#999">compared to previous</small>
                `;
                container.appendChild(item);
            });
        } else {
            container.innerHTML = '<p style="padding:10px; color:#888;">No significant changes detected or insufficient data.</p>';
        }
    } catch (e) {
        container.innerHTML = '<p style="padding:10px; color:red;">Could not load history.</p>';
    }
}

// --- CHAT & CHARTS ---
let myChart = null;
function renderRiskChart(data) {
    const ctx = document.getElementById('riskChart').getContext('2d');
    if (myChart) myChart.destroy();

    // Gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    const color = data.probability > 50 ? '#dc3545' : '#198754';

    myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Risk', 'Health'],
            datasets: [{
                data: [data.probability, 100 - data.probability],
                backgroundColor: [color, '#e9ecef'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function toggleChat() {
    document.getElementById('chat-window').classList.toggle('open');
}

function handleChatInput(e) {
    if (e.key === 'Enter') sendMessage();
}

function sendMessage() {
    const input = document.getElementById('chat-input');
    const msg = input.value;
    if (!msg) return;

    const div = document.createElement('div');
    div.className = 'message user';
    div.innerText = msg;
    document.getElementById('chat-messages').appendChild(div);
    input.value = '';

    // Scroll to bottom
    const container = document.getElementById('chat-messages');
    container.scrollTop = container.scrollHeight;

    setTimeout(() => {
        const botDiv = document.createElement('div');
        botDiv.className = 'message bot';

        // Simple responses
        let reply = "I'm a demo bot. Please consult a specialist.";
        if (msg.toLowerCase().includes('diet')) reply = "A balanced diet low in processed sugars is recommended for PCOS.";
        if (msg.toLowerCase().includes('symptom')) reply = "Common symptoms include irregular periods and weight gain.";

        botDiv.innerText = reply;
        document.getElementById('chat-messages').appendChild(botDiv);
        container.scrollTop = container.scrollHeight;
    }, 1000);
}

function locateDoctors() {
    // Just a placeholder for the demo tab switch
    alert("Navigating to Doctor Finder Map (Not implemented in this view for clarity)");
}
