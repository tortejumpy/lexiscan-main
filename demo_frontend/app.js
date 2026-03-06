/**
 * LexiScan Auto — Demo Frontend JavaScript
 * Handles all 3 scenario interactions
 */

// Dynamically resolve API base: same host in production, localhost:8000 in local dev
const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000'
    : window.location.origin;

/* ════════════════════════════════════════
   SCENARIO SWITCHING
════════════════════════════════════════ */
function switchScenario(num) {
    [1, 2, 3].forEach(n => {
        document.getElementById(`scenario${n}`).classList.add('hidden');
        document.getElementById(`scenario${n}`).classList.remove('active');
        document.getElementById(`tab${n}`).classList.remove('active');
    });
    document.getElementById(`scenario${num}`).classList.remove('hidden');
    document.getElementById(`scenario${num}`).classList.add('active');
    document.getElementById(`tab${num}`).classList.add('active');
}

/* ════════════════════════════════════════
   SCENARIO 1 — DEMO SCRIPT SIMULATION
════════════════════════════════════════ */

// Sample contracts to simulate demo.py output
const SAMPLE_CONTRACTS = [
    {
        name: 'ABILITYINC_06_15_2020-EX-4.25-SERVICES AGREEMENT.txt',
        entities: {
            PARTY: [
                { text: 'TELCOSTAR PTE, LTD.', confidence: 0.91 },
                { text: 'Ability Computer & Software Industries Ltd', confidence: 0.87 },
                { text: 'McDermott Will & Emery LLP', confidence: 0.82 },
                { text: 'Provider Representatives', confidence: 0.79 }
            ],
            DATE: [
                { text: 'October 1, 2019', confidence: 0.97 },
                { text: 'November 1, 2019', confidence: 0.96 },
                { text: 'December 31, 2020', confidence: 0.95 },
                { text: 'December 31, 2021', confidence: 0.93 }
            ],
            AMOUNT: [
                { text: '$500,000 USD', confidence: 0.94 },
                { text: '10% service fee', confidence: 0.88 },
                { text: '15 days', confidence: 0.82 }
            ],
            JURISDICTION: [
                { text: 'State of Israel', confidence: 0.95 },
                { text: 'Singapore', confidence: 0.91 }
            ],
            TERM: [
                { text: '90 days', confidence: 0.88 },
                { text: '30 days', confidence: 0.84 },
                { text: 'three months', confidence: 0.81 }
            ]
        }
    },
    {
        name: 'ADAMSGOLFINC_03_21_2005-EX-10.17-ENDORSEMENT AGREEMENT.txt',
        entities: {
            PARTY: [
                { text: 'Adams Golf, Inc.', confidence: 0.93 },
                { text: 'Nantz Communications, Inc.', confidence: 0.90 },
                { text: 'Jim Nantz', confidence: 0.88 }
            ],
            DATE: [
                { text: 'March 21, 2005', confidence: 0.97 },
                { text: 'January 1, 2006', confidence: 0.95 },
                { text: 'December 31, 2008', confidence: 0.94 }
            ],
            AMOUNT: [
                { text: '$250,000 per year', confidence: 0.92 },
                { text: '$1,000,000', confidence: 0.90 }
            ],
            JURISDICTION: [
                { text: 'State of Texas', confidence: 0.91 },
                { text: 'United States', confidence: 0.87 }
            ],
            TERM: [
                { text: '3 years', confidence: 0.93 },
                { text: '30 days written notice', confidence: 0.84 }
            ]
        }
    },
    {
        name: 'ACCURAYINC_09_01_2010-EX-10.31-DISTRIBUTOR AGREEMENT.txt',
        entities: {
            PARTY: [
                { text: 'Accuray Incorporated', confidence: 0.94 },
                { text: 'Siemens Medical Solutions', confidence: 0.91 },
                { text: 'Accuray International', confidence: 0.85 }
            ],
            DATE: [
                { text: 'September 1, 2010', confidence: 0.97 },
                { text: 'August 31, 2015', confidence: 0.94 }
            ],
            AMOUNT: [
                { text: '$5,000,000', confidence: 0.95 },
                { text: 'USD 2,500,000', confidence: 0.91 },
                { text: '15% commission', confidence: 0.87 }
            ],
            JURISDICTION: [
                { text: 'State of California', confidence: 0.93 },
                { text: 'European Union', confidence: 0.86 }
            ],
            TERM: [
                { text: '5 years', confidence: 0.92 },
                { text: 'successive 1 year periods', confidence: 0.85 },
                { text: '60 days', confidence: 0.82 }
            ]
        }
    }
];

let demoRunning = false;

async function runDemo() {
    if (demoRunning) return;
    demoRunning = true;

    const btn = document.getElementById('runDemoBtn');
    const body = document.getElementById('terminalBody');
    btn.disabled = true;
    btn.textContent = '⏳ Running...';
    body.innerHTML = '';

    const delay = (ms) => new Promise(r => setTimeout(r, ms));

    const append = (html, className = '') => {
        const line = document.createElement('div');
        if (className) line.className = className;
        line.innerHTML = html;
        body.appendChild(line);
        body.scrollTop = body.scrollHeight;
    };

    const typeLines = async (lines, delayMs = 60) => {
        for (const [html, cls, wait] of lines) {
            append(html, cls);
            await delay(wait ?? delayMs);
        }
    };

    // Header
    await typeLines([
        ['<span class="t-separator">══════════════════════════════════════════════════════════════════════</span>', '', 80],
        ['<span class="t-heading">LexiScan Auto — Intelligent Legal Document Parser</span>', '', 80],
        ['<span class="t-separator">══════════════════════════════════════════════════════════════════════</span>', '', 120],
        ['', '', 80],
        ['<span class="t-info">[INFO] Initializing BaselineNERModel...</span>', '', 150],
        ['<span class="t-info">[INFO]   Creating RegexExtractor...</span>', '', 100],
        ['<span class="t-info">[INFO]     - Loading date patterns</span>', '', 80],
        ['<span class="t-info">[INFO]     - Loading amount patterns</span>', '', 80],
        ['<span class="t-info">[INFO]     - Loading jurisdiction patterns</span>', '', 80],
        ['<span class="t-info">[INFO]     - Loading party patterns</span>', '', 80],
        ['<span class="t-info">[INFO]     - Loading term patterns</span>', '', 100],
        ['<span class="t-info">[INFO]   Creating TFIDFClassifier...</span>', '', 120],
        ['<span class="t-info">[INFO]     - Setting up vectorizer (max 5000 features)</span>', '', 80],
        ['<span class="t-info">[INFO]     - Setting up logistic regression classifier</span>', '', 100],
        ['<span class="t-success">[INFO] BaselineNERModel initialized successfully ✓</span>', '', 150],
        ['', '', 100],
        ['<span class="t-info">[INFO] Scanning: data/raw/full_contract_txt/</span>', '', 120],
        ['<span class="t-success">[INFO] Found 3 contracts to process ✓</span>', '', 150],
        ['', '', 80],
    ]);

    // Process each contract
    const allResults = [];
    for (let i = 0; i < SAMPLE_CONTRACTS.length; i++) {
        const c = SAMPLE_CONTRACTS[i];
        const totalEntities = Object.values(c.entities).flat().length;

        await typeLines([
            [`<span class="t-separator">══════════════════════════════════════════════════════════════════════</span>`, '', 60],
            [`<span class="t-heading">Contract ${i + 1}/3: ${c.name}</span>`, '', 80],
            [`<span class="t-separator">══════════════════════════════════════════════════════════════════════</span>`, '', 80],
            ['', '', 60],
            [`<span class="t-info">[INFO] Opening: ${c.name}</span>`, '', 100],
            [`<span class="t-info">[INFO] Reading text content...</span>`, '', 180],
            [`<span class="t-info">[INFO] Running regex patterns on text...</span>`, '', 200],
            [`<span class="t-info">[INFO] Checking for overlapping entities...</span>`, '', 180],
            [`<span class="t-info">[INFO] Sorting entities by document position...</span>`, '', 150],
            ['', '', 80],
            [`<span class="t-success">Found <strong>${totalEntities}</strong> entities:</span>`, '', 100],
            ['', '', 60],
        ]);

        for (const [label, items] of Object.entries(c.entities)) {
            const colorClass = {
                PARTY: 't-party', DATE: 't-date', AMOUNT: 't-amount',
                JURISDICTION: 't-jurisdiction', TERM: 't-term'
            }[label] || 't-value';

            append(`<span class="${colorClass}">  ${label}: ${items.length} entities</span>`);
            await delay(80);

            const examples = items.slice(0, 2);
            for (const ex of examples) {
                const short = ex.text.length > 45 ? ex.text.slice(0, 45) + '...' : ex.text;
                append(`<span class="t-info">    → ${short} <span style="color:var(--text3)">(confidence: ${ex.confidence.toFixed(2)})</span></span>`);
                await delay(60);
            }
            append('');
            await delay(40);
        }

        allResults.push(c);
        await delay(100);
    }

    // Final summary
    await typeLines([
        ['', '', 60],
        ['<span class="t-separator">══════════════════════════════════════════════════════════════════════</span>', '', 80],
        ['<span class="t-success">✓  Demo completed successfully!</span>', '', 80],
        ['<span class="t-separator">══════════════════════════════════════════════════════════════════════</span>', '', 80],
        ['', '', 80],
        [`<span class="t-info">Processed: 3 contracts</span>`, '', 80],
        [`<span class="t-info">Total entities extracted: ${SAMPLE_CONTRACTS.reduce((sum, c) => sum + Object.values(c.entities).flat().length, 0)}</span>`, '', 80],
        [`<span class="t-info">Models used: BaselineNERModel (regex + tfidf)</span>`, '', 80],
        ['<span class="t-cursor"></span>', '', 0],
    ]);

    // Show visual results below
    renderDemoResults(SAMPLE_CONTRACTS);

    btn.disabled = false;
    btn.textContent = '▶ Run Again';
    demoRunning = false;
}

function renderDemoResults(contracts) {
    const container = document.getElementById('demoResults');
    container.classList.remove('hidden');

    const colorOf = label => ({
        PARTY: '#818cf8', DATE: '#22d3ee', AMOUNT: '#10b981',
        JURISDICTION: '#f59e0b', TERM: '#f43f5e'
    }[label] || '#94a3b8');

    const chipClass = label => ({
        PARTY: 'chip-party', DATE: 'chip-date', AMOUNT: 'chip-amount',
        JURISDICTION: 'chip-jurisdiction', TERM: 'chip-term'
    }[label] || '');

    container.innerHTML = `
    <div class="demo-results-header">
      <span style="font-size:1.2rem">📊</span>
      <span class="demo-results-title">Extraction Results — 3 Contracts Processed</span>
      <span class="status-badge status-passed">PASSED</span>
    </div>
    <div class="demo-results-body">
      <div class="results-grid">
        ${contracts.map(c => `
          <div class="result-contract-card">
            <div class="rcc-header" title="${c.name}">${c.name}</div>
            <div class="rcc-body">
              ${Object.entries(c.entities).map(([label, items]) => `
                <div class="entity-type-row">
                  <span class="entity-type-label" style="color:${colorOf(label)}">${label}</span>
                  <span class="entity-type-count">${items.length}</span>
                </div>
                <div class="entity-examples">
                  ${items.slice(0, 3).map(e => `<span class="entity-chip ${chipClass(label)}" title="${e.text}">${e.text}</span>`).join('')}
                </div>
              `).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    </div>`;

    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/* ════════════════════════════════════════
   SCENARIO 2 — REST API
════════════════════════════════════════ */

async function checkHealth() {
    const container = document.getElementById('healthResult');
    container.innerHTML = `<div style="display:flex;align-items:center;gap:8px;padding:14px 0;color:var(--text3)"><div class="spinner"></div> Pinging GET /health...</div>`;

    try {
        const res = await fetch(`${API_BASE}/health`);
        const data = await res.json();

        const modelsHtml = Object.entries(data.models_loaded || {}).map(([name, loaded]) => `
      <div class="health-item">
        <div class="health-item-name">${name.replace('_', ' ')}</div>
        <div class="health-item-status">${loaded ? '✅' : '❌'}</div>
      </div>
    `).join('');

        container.innerHTML = `
      <div style="padding:12px 16px 0; display:flex; align-items:center; gap:8px;">
        <span style="color:#4ade80;font-weight:700;font-size:0.9rem;">● ${data.status?.toUpperCase() ?? 'HEALTHY'}</span>
        <span style="color:var(--text3);font-size:0.8rem;font-family:'JetBrains Mono',monospace;">v${data.version}</span>
      </div>
      <div class="health-grid">${modelsHtml}</div>
    `;
        showToast('✅ Server is healthy', 'success');
    } catch (err) {
        container.innerHTML = `
      <div style="padding:14px 16px;color:#f87171;font-size:0.85rem;">
        ❌ Cannot reach server at ${API_BASE}<br/>
        <span style="color:var(--text3);font-size:0.78rem;">Make sure uvicorn is running: <code style="color:#a5b4fc">python -m uvicorn src.api.main:app --reload</code></span>
      </div>`;
        showToast('Server unreachable — is uvicorn running?', 'error');
    }
}

let selectedFile = null;

function handleDragOver(e) {
    e.preventDefault();
    document.getElementById('uploadArea').classList.add('drag-over');
}
function handleDragLeave(e) {
    document.getElementById('uploadArea').classList.remove('drag-over');
}
function handleFileDrop(e) {
    e.preventDefault();
    document.getElementById('uploadArea').classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) setSelectedFile(file);
}
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) setSelectedFile(file);
}
function setSelectedFile(file) {
    const nameLower = file.name.toLowerCase();
    const isPdf = nameLower.endsWith('.pdf');
    const isTxt = nameLower.endsWith('.txt');
    if (!isPdf && !isTxt) {
        showToast('Only .txt and .pdf files are supported', 'error');
        return;
    }
    selectedFile = file;
    const info = document.getElementById('selectedFile');
    const icon = isPdf ? '📕' : '📄';
    const type = isPdf ? 'PDF' : 'TXT';
    info.textContent = `${icon} ${file.name}  (${type} · ${(file.size / 1024).toFixed(1)} KB)`;
    info.classList.remove('hidden');
    document.getElementById('extractBtn').disabled = false;
}

async function uploadAndExtract() {
    if (!selectedFile) return;

    const btn = document.getElementById('extractBtn');
    const loader = document.getElementById('extractLoader');
    btn.disabled = true;
    btn.querySelector('.btn-text').textContent = 'Extracting...';
    loader.classList.remove('hidden');

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const res = await fetch(`${API_BASE}/extract?model=baseline`, {
            method: 'POST',
            body: formData
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Extraction failed');
        }

        const data = await res.json();
        renderAPIResults(data);
        showToast(`Extracted ${Object.values(data.entities).flat().length} entities`, 'success');
    } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
        document.getElementById('apiResults').innerHTML = `
      <div class="api-results-header"><span class="api-results-title">❌ Extraction Failed</span></div>
      <div class="api-results-body" style="color:#f87171;font-size:0.85rem;">${err.message}</div>`;
        document.getElementById('apiResults').classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.querySelector('.btn-text').textContent = 'Extract Entities';
        loader.classList.add('hidden');
    }
}

function renderAPIResults(data) {
    const container = document.getElementById('apiResults');
    container.classList.remove('hidden');

    const statusClass = {
        PASSED: 'status-passed', WARNING: 'status-warning', FAILED: 'status-failed'
    }[data.validation_status] || 'status-passed';

    const totalEntities = Object.values(data.entities).flat().length;

    const colorOf = label => ({
        PARTY: '#818cf8', DATE: '#22d3ee', AMOUNT: '#10b981',
        JURISDICTION: '#f59e0b', TERM: '#f43f5e'
    }[label] || '#94a3b8');

    const bgOf = label => ({
        PARTY: 'rgba(129,140,248,0.08)', DATE: 'rgba(34,211,238,0.08)',
        AMOUNT: 'rgba(16,185,129,0.08)', JURISDICTION: 'rgba(245,158,11,0.08)',
        TERM: 'rgba(244,63,94,0.08)'
    }[label] || 'var(--surface2)');

    const entitiesHtml = Object.entries(data.entities).map(([label, items]) => `
    <div class="entities-section">
      <div class="entities-type-header" style="color:${colorOf(label)}">
        <span>${label}</span>
        <span>${items.length} found</span>
      </div>
      ${items.map(e => `
        <div class="entity-item" style="background:${bgOf(label)}; border-left: 3px solid ${colorOf(label)}">
          <div class="entity-text">${e.text}</div>
          <div class="entity-meta">
            <div class="entity-conf" style="color:${colorOf(label)}">${(e.confidence * 100).toFixed(0)}%</div>
            <div>${e.method}</div>
          </div>
        </div>
      `).join('')}
    </div>
  `).join('');

    const datesHtml = data.dates ? Object.entries(data.dates).map(([key, d]) => `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 10px;background:var(--surface2);border-radius:6px;margin-bottom:4px;font-size:0.82rem;">
      <span style="color:var(--text3);text-transform:capitalize">${key.replace('_', ' ')}</span>
      <span style="color:#67e8f9;font-family:'JetBrains Mono',monospace">${d.text}</span>
      ${d.iso ? `<span style="color:var(--text3);font-family:'JetBrains Mono',monospace">${d.iso}</span>` : ''}
    </div>
  `).join('') : '';

    container.innerHTML = `
    <div class="api-results-header">
      <span class="api-results-title">📋 Extraction Results — ${data.document_id}</span>
      <span class="status-badge ${statusClass}">${data.validation_status}</span>
    </div>
    <div class="api-results-body">
      <div class="api-meta">
        <div class="api-meta-item"><strong>${totalEntities}</strong> entities extracted</div>
        <div class="api-meta-item">⏱ <strong>${data.processing_time_ms?.toFixed(1) ?? '—'}</strong> ms</div>
        <div class="api-meta-item">Model: <strong>${data.model_used}</strong></div>
      </div>
      ${datesHtml ? `<div style="margin-bottom:14px"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.07em;color:var(--text3);font-weight:600;margin-bottom:8px">Categorized Dates</div>${datesHtml}</div>` : ''}
      ${entitiesHtml}
      ${data.validation_errors?.length ? `<div style="margin-top:10px;font-size:0.8rem;color:#fda4af"><strong>Errors:</strong> ${data.validation_errors.join(', ')}</div>` : ''}
      ${data.validation_warnings?.length ? `<div style="margin-top:6px;font-size:0.8rem;color:#fde68a"><strong>Warnings:</strong> ${data.validation_warnings.join(', ')}</div>` : ''}
    </div>`;

    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/* ════════════════════════════════════════
   SCENARIO 3 — PYTHON SDK PLAYGROUND
════════════════════════════════════════ */

async function extractFromText() {
    const text = document.getElementById('playgroundText').value.trim();
    if (!text) {
        showToast('Please paste some contract text first', 'error');
        return;
    }

    const btn = document.getElementById('playgroundBtnText');
    btn.textContent = '⏳ Extracting...';

    try {
        // Create a blob from the text and send as a file
        const blob = new Blob([text], { type: 'text/plain' });
        const file = new File([blob], 'playground_contract.txt', { type: 'text/plain' });
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(`${API_BASE}/extract?model=baseline`, {
            method: 'POST',
            body: formData
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Extraction failed');
        }

        const data = await res.json();
        renderPlaygroundResults(data);
        showToast(`Found ${Object.values(data.entities).flat().length} entities`, 'success');
    } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
        const container = document.getElementById('playgroundResults');
        container.classList.remove('hidden');
        container.innerHTML = `
      <div class="playground-results-header">❌ Error</div>
      <div class="playground-results-body" style="color:#f87171;font-size:0.85rem;">${err.message}<br><span style="color:var(--text3)">Make sure the API server is running at port 8000</span></div>`;
    } finally {
        btn.textContent = '⚡ Extract via API';
    }
}

function renderPlaygroundResults(data) {
    const container = document.getElementById('playgroundResults');
    container.classList.remove('hidden');

    const totalEntities = Object.values(data.entities).flat().length;
    const colorOf = label => ({
        PARTY: '#818cf8', DATE: '#22d3ee', AMOUNT: '#10b981',
        JURISDICTION: '#f59e0b', TERM: '#f43f5e'
    }[label] || '#94a3b8');

    const chipClass = label => ({
        PARTY: 'chip-party', DATE: 'chip-date', AMOUNT: 'chip-amount',
        JURISDICTION: 'chip-jurisdiction', TERM: 'chip-term'
    }[label] || '');

    const statusClass = {
        PASSED: 'status-passed', WARNING: 'status-warning', FAILED: 'status-failed'
    }[data.validation_status] || 'status-passed';

    const entitySummary = Object.entries(data.entities).map(([label, items]) => `
    <div style="margin-bottom:12px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
        <span style="font-size:0.78rem;font-weight:700;font-family:'JetBrains Mono',monospace;color:${colorOf(label)}">${label}</span>
        <span style="font-size:0.72rem;color:var(--text3)">${items.length} found</span>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:4px">
        ${items.map(e => `<span class="entity-chip ${chipClass(label)}" title="${e.text}">${e.text.length > 30 ? e.text.slice(0, 30) + '…' : e.text}</span>`).join('')}
      </div>
    </div>
  `).join('');

    // Also show what the Python print loop would output
    const printOutput = Object.entries(data.entities).flatMap(([, items]) =>
        items.map(e => `<span style="color:${colorOf(e.label)}">${e.label}</span><span style="color:var(--text3)">: </span><span style="color:#e2e8f0">${e.text}</span>`)
    ).join('\n');

    container.innerHTML = `
    <div class="playground-results-header" style="display:flex;justify-content:space-between;align-items:center">
      <span>🐍 Python Output Simulation</span>
      <span class="status-badge ${statusClass}">${data.validation_status}</span>
    </div>
    <div class="playground-results-body">
      <div style="font-size:0.72rem;color:var(--text3);text-transform:uppercase;letter-spacing:0.07em;font-weight:600;margin-bottom:10px">
        ${totalEntities} entities · ${data.processing_time_ms?.toFixed(1) ?? '—'} ms
      </div>
      ${entitySummary}
      <div style="margin-top:14px">
        <div style="font-size:0.72rem;color:var(--text3);text-transform:uppercase;letter-spacing:0.07em;font-weight:600;margin-bottom:8px">
          Console output (print loop)
        </div>
        <div class="json-display" style="font-size:0.78rem;line-height:1.8">${printOutput}</div>
      </div>
    </div>`;

    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/* ════════════════════════════════════════
   UTILITY: Copy Code
════════════════════════════════════════ */
function copyCode() {
    const code = `# my_script.py
from src.models.baseline import BaselineNERModel

# Initialize the NER model
model = BaselineNERModel()

# Read a contract file
with open("contract.txt", "r") as f:
    text = f.read()

# Extract named entities
entities = model.extract_entities(text)

# Process results
for entity in entities:
    print(f"{entity['label']}: {entity['text']}")`;

    navigator.clipboard.writeText(code)
        .then(() => showToast('Code copied to clipboard!', 'success'))
        .catch(() => showToast('Could not copy code', 'error'));
}

/* ════════════════════════════════════════
   TOAST NOTIFICATIONS
════════════════════════════════════════ */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

/* ════════════════════════════════════════
   INIT
════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
    // Check if Server is reachable and update badge
    fetch(`${API_BASE}/health`)
        .then(r => r.json())
        .then(data => {
            showToast(`✅ API Server connected — v${data.version}`, 'success');
        })
        .catch(() => {
            showToast('⚠️ API server not detected on port 8000', 'error');
        });
});
