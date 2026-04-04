// Glass Box Explorer - Main JavaScript

const API_BASE = 'http://localhost:8080/api';

// State
let currentTab = 'signals';
let signals = [];
let agents = [];
let owners = [];
let selectedOwner = 'all';
let currentPage = 1;
const itemsPerPage = 5;

// ============================================================================
// Toast Notification System
// ============================================================================

function showToast(message, type = 'info', title = null) {
    const container = document.getElementById('toast-container');

    const icons = {
        error: '❌',
        success: '✅',
        info: 'ℹ️',
        warning: '⚠️'
    };

    const titles = {
        error: title || 'Error',
        success: title || 'Success',
        info: title || 'Info',
        warning: title || 'Warning'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-icon">${icons[type]}</div>
        <div class="toast-content">
            <div class="toast-title">${titles[type]}</div>
            <div class="toast-message">${message}</div>
        </div>
        <div class="toast-close" onclick="dismissToast(this)">×</div>
    `;

    container.appendChild(toast);

    // Auto dismiss after 5 seconds
    setTimeout(() => {
        dismissToast(toast.querySelector('.toast-close'));
    }, 5000);
}

function dismissToast(closeBtn) {
    const toast = closeBtn.parentElement;
    toast.classList.add('removing');
    setTimeout(() => {
        toast.remove();
    }, 300);
}

// ============================================================================
// Tab Switching
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Setup tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;
            switchTab(tabId);
        });
    });

    // Setup owner filter
    const ownerFilter = document.getElementById('owner-filter');
    if (ownerFilter) {
        ownerFilter.addEventListener('change', (e) => {
            selectedOwner = e.target.value;
            currentPage = 1;  // Reset to first page
            loadSignals();
        });
    }

    // Initial load
    loadOwners();
    loadSignals();
    loadAgents();
});

function switchTab(tabId) {
    currentTab = tabId;

    // Update buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabId) {
            btn.classList.add('active');
        }
    });

    // Update panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.getElementById(tabId).classList.add('active');

    // Load data for workflow tab
    if (tabId === 'workflow') {
        refreshWorkflow();
    }
}

// ============================================================================
// Owners
// ============================================================================

async function loadOwners() {
    try {
        const response = await fetch(`${API_BASE}/owners`);
        const data = await response.json();

        if (data.success) {
            owners = data.owners || [];
            populateOwnerFilter(owners);
        }
    } catch (error) {
        console.error('Error loading owners:', error);
    }
}

function populateOwnerFilter(ownersList) {
    const ownerFilter = document.getElementById('owner-filter');
    if (!ownerFilter) return;

    // Clear all options
    ownerFilter.innerHTML = '';

    // Add owner options (just addresses)
    ownersList.forEach(owner => {
        const option = document.createElement('option');
        option.value = owner.address;
        option.textContent = owner.address;
        ownerFilter.appendChild(option);
    });

    // Select first owner by default if available
    if (ownersList.length > 0) {
        selectedOwner = ownersList[0].address;
        ownerFilter.value = selectedOwner;
    }
}

// ============================================================================
// Signals Tab
// ============================================================================

async function loadSignals() {
    try {
        const params = new URLSearchParams();
        if (selectedOwner && selectedOwner !== 'all') {
            params.append('owner', selectedOwner);
        }

        const url = `${API_BASE}/signals${params.toString() ? '?' + params.toString() : ''}`;
        const response = await fetch(url);
        const data = await response.json();

        signals = data.signals || [];
        updateSignalStats(signals);
        renderSignals(signals);
    } catch (error) {
        console.error('Error loading signals:', error);
        document.getElementById('signals-list').innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <p>Error loading signals from SUI network</p>
                <p style="font-size: 12px; margin-top: 10px;">${error.message}</p>
            </div>
        `;
    }
}

function updateSignalStats(signalsData) {
    const newsCount = signalsData.filter(t => t.signal_type === 'news').length;
    const priceCount = signalsData.filter(t => t.signal_type === 'price').length;
    const insightCount = signalsData.filter(t => t.signal_type === 'insight').length;

    // Get latest timestamp
    const timestamps = signalsData.map(t => new Date(t.timestamp));
    const latest = timestamps.length > 0 ? new Date(Math.max(...timestamps)) : null;

    document.getElementById('total-signals').textContent = signalsData.length;
    document.getElementById('news-signals').textContent = newsCount;
    document.getElementById('price-signals').textContent = priceCount;
    document.getElementById('insight-signals').textContent = insightCount;
    document.getElementById('latest-update').textContent = latest
        ? formatTimeAgo(latest)
        : 'N/A';
}

function renderSignals(signalsToRender) {
    const container = document.getElementById('signals-list');

    if (signalsToRender.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <p>No signals found on SUI network</p>
            </div>
        `;
        return;
    }

    // Pagination
    const totalPages = Math.ceil(signalsToRender.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedSignals = signalsToRender.slice(startIndex, endIndex);

    // Render signals
    const signalsHTML = paginatedSignals.map(signal => {
        return createSignalCard(signal);
    }).join('');

    // Render pagination controls
    const paginationHTML = totalPages > 1 ? `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding: 15px; background: #1a1a1a; border-radius: 8px;">
            <button
                onclick="changePage(${currentPage - 1})"
                ${currentPage === 1 ? 'disabled' : ''}
                style="padding: 8px 16px; background: ${currentPage === 1 ? '#333' : '#4CAF50'}; color: white; border: none; border-radius: 4px; cursor: ${currentPage === 1 ? 'not-allowed' : 'pointer'};">
                ← Previous
            </button>
            <span style="color: #ccc;">
                Page ${currentPage} of ${totalPages} (${signalsToRender.length} total items)
            </span>
            <button
                onclick="changePage(${currentPage + 1})"
                ${currentPage === totalPages ? 'disabled' : ''}
                style="padding: 8px 16px; background: ${currentPage === totalPages ? '#333' : '#4CAF50'}; color: white; border: none; border-radius: 4px; cursor: ${currentPage === totalPages ? 'not-allowed' : 'pointer'};">
                Next →
            </button>
        </div>
    ` : '';

    container.innerHTML = signalsHTML + paginationHTML;
}

function changePage(newPage) {
    currentPage = newPage;
    filterSignals();
}

function createSignalCard(signal) {
    let typeClass = 'insight';
    if (signal.signal_type === 'news') typeClass = 'news';
    else if (signal.signal_type === 'price') typeClass = 'price';

    // For price signals, display the symbol and price
    let priceDisplay = '';
    if (signal.signal_type === 'price' && signal.symbol && signal.price_usd) {
        priceDisplay = `
            <div class="signal-field" style="background: #2a2a2a; padding: 12px; border-radius: 6px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 16px; font-weight: bold; color: #4CAF50;">
                        ${signal.symbol}
                    </div>
                    <div style="font-size: 20px; font-weight: bold;">
                        $${parseFloat(signal.price_usd).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                    </div>
                </div>
            </div>
        `;
    }

    return `
        <div class="signal-card" data-signal-id="${signal.signal_id || 'unknown'}">
            <div class="signal-header">
                <span class="signal-type ${typeClass}">${signal.signal_type}</span>
                <span class="signal-timestamp">${formatTimestamp(signal.timestamp)}</span>
            </div>
            <div class="signal-body">
                ${priceDisplay}
                <div class="signal-field">
                    <div class="field-label">Signal ID</div>
                    <div class="field-value">${signal.signal_id || 'N/A'}</div>
                </div>
                <div class="signal-field">
                    <div class="field-label">SUI Object ID</div>
                    <div class="field-value">${truncate(signal.object_id || 'N/A', 32)}</div>
                </div>
                <div class="signal-field">
                    <div class="field-label">Walrus Blob ID</div>
                    <div class="field-value">${truncate(signal.walrus_blob_id || 'N/A', 32)}</div>
                </div>
                <div class="signal-field">
                    <div class="field-label">Owner</div>
                    <div class="field-value">${truncate(signal.owner || 'default', 32)}</div>
                </div>
                <div class="signal-field">
                    <div class="field-label">Producer</div>
                    <div class="field-value">${signal.producer || 'N/A'}</div>
                </div>
                <div class="signal-field">
                    <div class="field-label">Size</div>
                    <div class="field-value">${formatBytes(signal.size_bytes || 0)}</div>
                </div>
            </div>
            ${signal.walrus_blob_id ? `
                <div style="margin-top: 12px; display: flex; gap: 10px;">
                    <button onclick="viewWalrusData('${signal.signal_id}')"
                            class="expand-btn"
                            style="flex: 1; padding: 10px;"
                            title="Fetch and view full data from Walrus">
                        📦 View Full Data
                    </button>
                    <a href="https://walruscan.com/testnet/blob/${signal.walrus_blob_id}"
                       target="_blank"
                       class="expand-btn"
                       style="text-decoration: none; flex: 1; text-align: center; padding: 10px;"
                       title="View on Walruscan explorer">
                        🔗 View on Walruscan
                    </a>
                </div>
            ` : ''}
        </div>
    `;
}

async function viewWalrusData(signalId) {
    try {
        showToast('Fetching full data from Walrus...', 'info', 'Loading');

        const response = await fetch(`${API_BASE}/signals/${signalId}/full`);
        const data = await response.json();

        if (!data.success) {
            showToast(data.error || 'Failed to fetch signal data', 'error', 'Fetch Failed');
            return;
        }

        // Show success and display data in modal
        showToast('Successfully fetched data from Walrus!', 'success');
        showWalrusDataModal(data);

        // Create a formatted view
        const articles = data.full_data?.articles || [];
        const count = articles.length;

        showToast(
            `Retrieved ${count} articles. Check browser console for full data.`,
            'info',
            'Data Retrieved'
        );
    } catch (error) {
        showToast(
            `Network error: ${error.message}. Check if the API server is running.`,
            'error',
            'Fetch Error'
        );
    }
}

function refreshSignals() {
    document.getElementById('signals-list').innerHTML = '<div class="loading">Refreshing...</div>';
    loadSignals();
}

// Filter signals
document.getElementById('signal-type-filter')?.addEventListener('change', (e) => {
    currentPage = 1;  // Reset to first page
    filterSignals();
});

document.getElementById('search-box')?.addEventListener('input', (e) => {
    currentPage = 1;  // Reset to first page
    filterSignals();
});

function filterSignals() {
    const typeFilter = document.getElementById('signal-type-filter').value;
    const searchQuery = document.getElementById('search-box').value.toLowerCase();

    let filtered = signals;

    // Filter by type
    if (typeFilter !== 'all') {
        filtered = filtered.filter(t => t.signal_type === typeFilter);
    }

    // Filter by search
    if (searchQuery) {
        filtered = filtered.filter(t => {
            const searchText = `
                ${t.signal_id}
                ${t.object_id}
                ${t.producer}
                ${t.signal_type || ''}
            `.toLowerCase();
            return searchText.includes(searchQuery);
        });
    }

    renderSignals(filtered);
}

// ============================================================================
// Agents Tab
// ============================================================================

async function loadAgents() {
    try {
        const response = await fetch(`${API_BASE}/agents`);
        const data = await response.json();

        agents = data.agents || [];
        renderAgents(agents);
    } catch (error) {
        console.error('Error loading agents:', error);
        document.getElementById('agents-grid').innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <p>Error loading agents</p>
                <p style="font-size: 12px; margin-top: 10px;">${error.message}</p>
            </div>
        `;
    }
}

function renderAgents(agentsToRender) {
    const container = document.getElementById('agents-grid');

    if (agentsToRender.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🤖</div>
                <p>No agents found</p>
            </div>
        `;
        return;
    }

    container.innerHTML = agentsToRender.map(agent => {
        return createAgentCard(agent);
    }).join('');
}

function createAgentCard(agent) {
    return `
        <div class="agent-card" onclick="viewAgentDetail('${agent.agent_id}')">
            <div class="agent-icon">${agent.icon || '🤖'}</div>
            <div class="agent-name">${agent.name}</div>
            <div class="agent-description">${agent.description}</div>
            <div class="agent-stats">
                <div>
                    <div class="agent-stat-label">Executions</div>
                    <div class="agent-stat-value">${agent.execution_count || 0}</div>
                </div>
                <div>
                    <div class="agent-stat-label">Avg Confidence</div>
                    <div class="agent-stat-value">${agent.avg_confidence ? (agent.avg_confidence * 100).toFixed(1) + '%' : 'N/A'}</div>
                </div>
            </div>
        </div>
    `;
}

async function viewAgentDetail(agentId) {
    try {
        showToast('Loading agent reasoning traces from Walrus...', 'info', 'Loading');

        // Fetch agent reasoning traces
        const response = await fetch(`${API_BASE}/agents/${agentId}/traces`);
        const data = await response.json();

        if (!data.success) {
            showToast(data.error || 'Failed to load agent traces', 'error', 'Load Failed');
            return;
        }

        renderAgentDetail(data);

        // Show modal
        document.getElementById('agent-detail-modal').classList.add('active');

        showToast(`Loaded ${data.traces_count} reasoning traces`, 'success');
    } catch (error) {
        showToast(
            `Network error: ${error.message}. Check if the API server is running.`,
            'error',
            'Load Error'
        );
    }
}

function renderAgentDetail(data) {
    const container = document.getElementById('agent-detail-content');

    const agent = data.agent;
    const traces = data.traces || [];

    container.innerHTML = `
        <h2>${agent.icon || '🤖'} ${agent.name}</h2>
        <p style="color: var(--text-secondary); margin-bottom: 20px;">${agent.description}</p>

        <h3>Reasoning Traces (${traces.length})</h3>
        <p style="font-size: 14px; color: var(--text-secondary); margin-bottom: 20px;">
            All traces pulled directly from Walrus decentralized storage
        </p>

        ${traces.map(trace => renderReasoningTrace(trace)).join('')}
    `;
}

function renderReasoningTrace(trace) {
    const steps = trace.reasoning_steps || [];

    return `
        <div class="reasoning-trace">
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                <div>
                    <strong>Trace ID:</strong> ${truncate(trace.walrus_blob_id || 'N/A', 32)}
                </div>
                <div>
                    <strong>Confidence:</strong> ${(trace.confidence * 100).toFixed(1)}%
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <div style="font-size: 12px; color: var(--text-secondary);">
                    ${formatTimestamp(trace.timestamp)}
                </div>
                ${trace.walrus_blob_id ? `
                    <a href="https://walruscan.com/testnet/blob/${trace.walrus_blob_id}"
                       target="_blank"
                       class="expand-btn"
                       style="text-decoration: none; padding: 8px 16px; font-size: 12px;"
                       title="View trace on Walruscan explorer">
                        🔗 View on Walruscan
                    </a>
                ` : ''}
            </div>

            <h4 style="margin-bottom: 15px;">Reasoning Steps (${steps.length})</h4>
            ${steps.map((step, i) => `
                <div class="reasoning-step">
                    <div class="step-header">
                        <span class="step-name">Step ${i + 1}: ${step.step_name || 'Unknown'}</span>
                        <span class="step-timestamp">${formatTimestamp(step.timestamp)}</span>
                    </div>
                    <div class="step-description">${step.description || ''}</div>
                    ${step.output ? `
                        <div class="step-data">
                            <pre>${JSON.stringify(step.output, null, 2)}</pre>
                        </div>
                    ` : ''}
                </div>
            `).join('')}

            ${trace.llm_prompt ? `
                <details style="margin-top: 15px;">
                    <summary style="cursor: pointer; color: var(--primary-color);">LLM Prompt & Response</summary>
                    <div class="step-data" style="margin-top: 10px;">
                        <strong>Prompt:</strong>
                        <pre>${trace.llm_prompt.substring(0, 500)}...</pre>
                        <br>
                        <strong>Response:</strong>
                        <pre>${trace.llm_response?.substring(0, 500) || 'N/A'}...</pre>
                    </div>
                </details>
            ` : ''}
        </div>
    `;
}

function closeAgentDetail() {
    document.getElementById('agent-detail-modal').classList.remove('active');
}

function refreshAgents() {
    document.getElementById('agents-grid').innerHTML = '<div class="loading">Refreshing...</div>';
    loadAgents();
}

// ============================================================================
// Utility Functions
// ============================================================================

function formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString();
}

function formatTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);

    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function truncate(str, maxLength) {
    if (!str || str.length <= maxLength) return str;
    return str.substring(0, maxLength) + '...';
}

// Show Walrus data in a modal
function showWalrusDataModal(data) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('walrus-data-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'walrus-data-modal';
        modal.className = 'modal';
        modal.style.display = 'none';
        document.body.appendChild(modal);
    }

    // Format the data as pretty JSON
    const fullData = data.full_data || {};
    const metadata = data.metadata || {};

    const jsonString = JSON.stringify(fullData, null, 2);

    modal.innerHTML = `
        <div class="modal-content" style="max-width: 900px; max-height: 80vh; overflow-y: auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; position: sticky; top: 0; background: #1a1a1a; padding-bottom: 15px; border-bottom: 1px solid #333;">
                <h2 style="margin: 0;">📦 Walrus Data</h2>
                <button onclick="closeWalrusDataModal()" style="background: #333; border: none; color: white; font-size: 24px; cursor: pointer; width: 30px; height: 30px; border-radius: 4px;">&times;</button>
            </div>

            <div style="margin-bottom: 20px;">
                <h3 style="color: #4CAF50; margin-bottom: 10px;">Metadata</h3>
                <div style="background: #2a2a2a; padding: 15px; border-radius: 6px; font-family: monospace; font-size: 13px;">
                    <div><strong>Signal ID:</strong> ${metadata.signal_id || 'N/A'}</div>
                    <div><strong>Type:</strong> ${metadata.signal_type || 'N/A'}</div>
                    <div><strong>Walrus Blob ID:</strong> ${metadata.walrus_blob_id || 'N/A'}</div>
                    <div><strong>Owner:</strong> ${metadata.owner || 'N/A'}</div>
                    <div><strong>Size:</strong> ${formatBytes(metadata.size_bytes || 0)}</div>
                </div>
            </div>

            <div>
                <h3 style="color: #4CAF50; margin-bottom: 10px;">Full Data from Walrus</h3>
                <pre style="background: #2a2a2a; padding: 15px; border-radius: 6px; overflow-x: auto; font-size: 12px; line-height: 1.5;">${jsonString}</pre>
            </div>

            <div style="margin-top: 20px; text-align: right;">
                <button onclick="copyToClipboard(${JSON.stringify(jsonString).replace(/'/g, "\\'")})" class="expand-btn" style="margin-right: 10px;">
                    📋 Copy JSON
                </button>
                <button onclick="closeWalrusDataModal()" class="expand-btn">
                    Close
                </button>
            </div>
        </div>
    `;

    modal.style.display = 'block';
}

function closeWalrusDataModal() {
    const modal = document.getElementById('walrus-data-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('JSON copied to clipboard!', 'success');
    }).catch(err => {
        showToast('Failed to copy: ' + err.message, 'error');
    });
}

// Close modal when clicking outside
window.onclick = function(event) {
    const agentModal = document.getElementById('agent-detail-modal');
    const walrusModal = document.getElementById('walrus-data-modal');
    const reasoningModal = document.getElementById('reasoning-ledger-modal');

    if (event.target === agentModal) {
        closeAgentDetail();
    }
    if (event.target === walrusModal) {
        closeWalrusDataModal();
    }
    if (event.target === reasoningModal) {
        closeReasoningLedger();
    }
}

// ========================================================================
// WORKFLOW TAB - Signal Lineage Visualization (Efficient Lazy Loading)
// ========================================================================

let workflowMetadata = null;  // Stores lightweight metadata (agents + signal IDs)
let currentLineageData = null;  // Stores the current signal's lineage data

async function refreshWorkflow() {
    try {
        // Fetch only lightweight metadata (agents + signal IDs)
        const response = await fetch(`${API_BASE}/workflow/metadata`);
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Failed to load workflow metadata');
        }

        workflowMetadata = data.agents;

        // Populate agent filter
        populateAgentFilterForWorkflow(workflowMetadata);

        // Clear signal filter and show instructions
        const signalFilter = document.getElementById('workflow-signal-filter');
        signalFilter.innerHTML = '<option value="all">Select an agent first</option>';
        signalFilter.disabled = true;

        // Show instructions
        showWorkflowInstructions();

        showToast('Workflow metadata loaded. Select an agent and signal to view lineage.', 'success');
    } catch (error) {
        console.error('Error refreshing workflow:', error);
        showToast('Failed to refresh workflow data', 'error');
    }
}

function populateAgentFilterForWorkflow(agents) {
    const agentFilter = document.getElementById('workflow-agent-filter');

    // Clear existing options
    agentFilter.innerHTML = '<option value="all">Select an agent...</option>';

    // Add agent options
    agents.forEach(agent => {
        const option = document.createElement('option');
        option.value = agent.agent_id;
        option.textContent = `${agent.name} (${agent.signal_count} signals)`;
        agentFilter.appendChild(option);
    });
}

function onAgentFilterChange() {
    if (!workflowMetadata) return;

    const agentFilter = document.getElementById('workflow-agent-filter').value;
    const signalFilter = document.getElementById('workflow-signal-filter');
    const viewButton = document.getElementById('view-lineage-btn');

    // When agent is selected, populate signal dropdown
    if (agentFilter !== 'all') {
        const selectedAgent = workflowMetadata.find(a => a.agent_id === agentFilter);

        if (selectedAgent) {
            // Populate signal filter with this agent's signals
            signalFilter.innerHTML = '<option value="all">Select a signal...</option>';
            signalFilter.disabled = false;

            selectedAgent.signals.forEach(signal => {
                const option = document.createElement('option');
                option.value = signal.signal_id;
                option.textContent = `${signal.insight_type || signal.signal_id} - ${new Date(signal.timestamp).toLocaleString()} (${(signal.confidence * 100).toFixed(0)}%)`;
                signalFilter.appendChild(option);
            });

            showWorkflowInstructions('Agent selected. Now select a signal to view its lineage.');

            // Disable button until signal is selected
            viewButton.disabled = true;
        }
    } else {
        // Reset signal filter and button
        signalFilter.innerHTML = '<option value="all">Select an agent first</option>';
        signalFilter.disabled = true;
        viewButton.disabled = true;
        showWorkflowInstructions();
    }
}

function onSignalFilterChange() {
    const signalFilter = document.getElementById('workflow-signal-filter');
    const viewButton = document.getElementById('view-lineage-btn');
    const selectedSignalId = signalFilter.value;

    // Enable button only when a specific signal is selected
    if (selectedSignalId !== 'all') {
        viewButton.disabled = false;
        showWorkflowInstructions('Signal selected. Click "View Lineage" to visualize the data flow.');
    } else {
        viewButton.disabled = true;
        showWorkflowInstructions('Agent selected. Now select a signal to view its lineage.');
    }
}

async function onViewLineageClick() {
    const signalFilter = document.getElementById('workflow-signal-filter');
    const selectedSignalId = signalFilter.value;

    if (selectedSignalId !== 'all') {
        await fetchAndDisplayLineage(selectedSignalId);
    }
}

function showWorkflowInstructions(message = null) {
    const graphContainer = document.getElementById('workflow-graph-container');

    const defaultMessage = `
        <div class="empty-state">
            <div class="empty-state-icon">🔄</div>
            <p>Select an agent and signal to view its lineage</p>
            <p style="font-size: 14px; color: var(--text-secondary); margin-top: 10px;">
                The workflow graph will show the data flow from data sources through agents
            </p>
        </div>
    `;

    const customMessage = `
        <div class="empty-state">
            <div class="empty-state-icon">ℹ️</div>
            <p>${message}</p>
        </div>
    `;

    graphContainer.innerHTML = message ? customMessage : defaultMessage;
}

async function fetchAndDisplayLineage(signalId) {
    try {
        showToast('Fetching signal lineage from Walrus...', 'info', 'Loading');

        // Fetch complete lineage for the selected signal
        const response = await fetch(`${API_BASE}/workflow/lineage/${signalId}`);
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Failed to fetch signal lineage');
        }

        currentLineageData = data;

        // Build and display graph from lineage data
        displayLineageGraph(data);

        showToast('Signal lineage loaded successfully', 'success');
    } catch (error) {
        console.error('Error fetching signal lineage:', error);
        showToast('Failed to fetch signal lineage', 'error');
        showWorkflowInstructions('Error loading lineage. Please try again.');
    }
}

function displayLineageGraph(lineageData) {
    const { signal, upstream_signals, reasoning_trace } = lineageData;

    // Build graph from lineage
    const graph = buildLineageGraph(signal, upstream_signals, reasoning_trace);

    // Render using D3.js
    renderWorkflowGraph(graph);
}

function buildLineageGraph(targetSignal, upstreamSignals, reasoningTrace) {
    const nodes = [];
    const edges = [];
    const nodeMap = new Map();

    // Add target agent node
    const targetAgent = {
        id: targetSignal.producer,
        label: formatAgentName(targetSignal.producer),
        type: 'agent',
        nodeType: targetSignal.producer,
        signal: targetSignal,
        reasoningTrace: reasoningTrace
    };
    nodes.push(targetAgent);
    nodeMap.set(targetAgent.id, targetAgent);

    // Add upstream signals as nodes/edges
    upstreamSignals.forEach(upstream => {
        let sourceNode;

        if (upstream.signal_type === 'price' || upstream.signal_type === 'news') {
            // Data source node
            const sourceId = `source_${upstream.signal_type}`;
            if (!nodeMap.has(sourceId)) {
                sourceNode = {
                    id: sourceId,
                    label: upstream.signal_type === 'news' ? 'News API' : 'Price Oracle',
                    type: 'data-source',
                    nodeType: upstream.signal_type
                };
                nodes.push(sourceNode);
                nodeMap.set(sourceId, sourceNode);
            } else {
                sourceNode = nodeMap.get(sourceId);
            }

            // Add edge from data source to target agent
            edges.push({
                source: sourceId,
                target: targetSignal.producer,
                signalType: upstream.signal_type,
                label: `${upstream.signal_type} Signal`,
                signal: upstream
            });
        } else if (upstream.signal_type === 'insight') {
            // Upstream agent node
            const upstreamAgentId = upstream.producer;
            if (!nodeMap.has(upstreamAgentId)) {
                sourceNode = {
                    id: upstreamAgentId,
                    label: formatAgentName(upstreamAgentId),
                    type: 'agent',
                    nodeType: upstreamAgentId,
                    signal: upstream
                };
                nodes.push(sourceNode);
                nodeMap.set(upstreamAgentId, sourceNode);
            } else {
                sourceNode = nodeMap.get(upstreamAgentId);
            }

            // Add edge from upstream agent to target agent
            edges.push({
                source: upstreamAgentId,
                target: targetSignal.producer,
                signalType: 'insight',
                label: `${upstream.insight_type} Insight`,
                signal: upstream
            });
        }
    });

    return { nodes, edges, targetSignal, reasoningTrace };
}

function formatAgentName(agentId) {
    return agentId.replace('agent_', 'Agent ').replace(/_/g, ' ').toUpperCase();
}

function renderWorkflowGraph(graph) {
    const svg = d3.select('#workflow-graph');
    svg.selectAll('*').remove(); // Clear previous graph

    const width = document.getElementById('workflow-graph-container').clientWidth - 40;
    const height = 600;

    svg.attr('width', width).attr('height', height);

    // Add arrow marker for edges
    svg.append('defs').append('marker')
        .attr('id', 'arrowhead')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 25)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#8899a6');

    // Create force simulation
    const simulation = d3.forceSimulation(graph.nodes)
        .force('link', d3.forceLink(graph.edges).id(d => d.id).distance(200))
        .force('charge', d3.forceManyBody().strength(-500))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(50));

    // Draw edges
    const edges = svg.append('g')
        .selectAll('path')
        .data(graph.edges)
        .enter()
        .append('path')
        .attr('class', d => `graph-edge ${d.signalType}-signal`)
        .attr('stroke-width', 2)
        .attr('fill', 'none')
        .attr('marker-end', 'url(#arrowhead)');

    // Draw edge labels
    const edgeLabels = svg.append('g')
        .selectAll('text')
        .data(graph.edges)
        .enter()
        .append('text')
        .attr('class', 'edge-label')
        .text(d => d.label);

    // Draw nodes
    const nodeGroups = svg.append('g')
        .selectAll('g')
        .data(graph.nodes)
        .enter()
        .append('g')
        .attr('class', d => `graph-node ${d.nodeType}`)
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended))
        .on('click', (event, d) => {
            if (d.type === 'agent') {
                showReasoningLedger(d);
            }
        });

    nodeGroups.append('circle')
        .attr('r', 30)
        .attr('stroke-width', 3);

    nodeGroups.append('text')
        .attr('dy', 45)
        .attr('text-anchor', 'middle')
        .text(d => d.label);

    // Update positions on simulation tick
    simulation.on('tick', () => {
        edges.attr('d', d => {
            const dx = d.target.x - d.source.x;
            const dy = d.target.y - d.source.y;
            return `M${d.source.x},${d.source.y} L${d.target.x},${d.target.y}`;
        });

        edgeLabels
            .attr('x', d => (d.source.x + d.target.x) / 2)
            .attr('y', d => (d.source.y + d.target.y) / 2);

        nodeGroups.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

async function showReasoningLedger(nodeData) {
    const modal = document.getElementById('reasoning-ledger-modal');
    const content = document.getElementById('reasoning-ledger-content');

    // Only show reasoning for agent nodes
    if (nodeData.type !== 'agent') {
        return;
    }

    content.innerHTML = '<div class="loading">Loading reasoning trace from Walrus...</div>';
    modal.style.display = 'flex';

    try {
        const reasoningTrace = nodeData.reasoningTrace;
        const signal = nodeData.signal;

        if (!reasoningTrace) {
            content.innerHTML = `
                <div class="reasoning-ledger-header">
                    <h3>Reasoning Ledger: ${nodeData.label}</h3>
                    <p style="color: var(--text-secondary);">No reasoning trace available for this execution</p>
                </div>
            `;
            return;
        }

        // Render reasoning trace
        let html = `
            <div class="reasoning-ledger-header">
                <h3>Reasoning Ledger: ${nodeData.label}</h3>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px;">
                    <div>
                        <div class="metadata-label">Execution Time</div>
                        <div class="metadata-value">${formatTimestamp(signal.timestamp)}</div>
                    </div>
                    <div>
                        <div class="metadata-label">Confidence</div>
                        <div class="metadata-value">${(signal.confidence * 100).toFixed(1)}%</div>
                    </div>
                    <div>
                        <div class="metadata-label">Insight Type</div>
                        <div class="metadata-value">${signal.insight_type || 'N/A'}</div>
                    </div>
                    <div>
                        <div class="metadata-label">Walrus Trace ID</div>
                        <div class="metadata-value">${signal.walrus_trace_id ? signal.walrus_trace_id.substring(0, 16) + '...' : 'N/A'}</div>
                    </div>
                </div>
            </div>
        `;

        // Render reasoning steps
        const steps = reasoningTrace.reasoning_steps || [];
        if (steps.length > 0) {
            html += `<h4 style="margin-top: 30px; margin-bottom: 15px;">Reasoning Steps (${steps.length})</h4>`;

            steps.forEach((step, i) => {
                html += `
                    <div class="reasoning-step">
                        <div class="step-header">
                            <span class="step-name">Step ${i + 1}: ${step.step_name || 'Unknown'}</span>
                            <span class="step-timestamp">${formatTimestamp(step.timestamp)}</span>
                        </div>
                        <div class="step-description">${step.description || ''}</div>
                        ${step.output ? `
                            <div class="step-data">
                                <pre>${JSON.stringify(step.output, null, 2)}</pre>
                            </div>
                        ` : ''}
                    </div>
                `;
            });
        }

        // Render LLM prompt/response if available
        if (reasoningTrace.llm_prompt) {
            html += `
                <details style="margin-top: 20px;">
                    <summary style="cursor: pointer; color: var(--primary-color); font-weight: bold;">
                        LLM Prompt & Response
                    </summary>
                    <div style="margin-top: 15px;">
                        <div class="step-data">
                            <strong>Prompt:</strong>
                            <pre>${reasoningTrace.llm_prompt.substring(0, 500)}${reasoningTrace.llm_prompt.length > 500 ? '...' : ''}</pre>
                        </div>
                        <div class="step-data" style="margin-top: 15px;">
                            <strong>Response:</strong>
                            <pre>${(reasoningTrace.llm_response || 'N/A').substring(0, 500)}${reasoningTrace.llm_response && reasoningTrace.llm_response.length > 500 ? '...' : ''}</pre>
                        </div>
                    </div>
                </details>
            `;
        }

        // Add link to Walruscan
        if (signal.walrus_trace_id) {
            html += `
                <div style="margin-top: 20px; text-align: center;">
                    <a href="https://walruscan.com/testnet/blob/${signal.walrus_trace_id}"
                       target="_blank"
                       class="expand-btn"
                       style="text-decoration: none; display: inline-block; padding: 12px 24px;">
                        🔗 View Full Trace on Walruscan
                    </a>
                </div>
            `;
        }

        content.innerHTML = html;

    } catch (error) {
        console.error('Error loading reasoning ledger:', error);
        content.innerHTML = `
            <div class="reasoning-ledger-header">
                <h3>Error</h3>
                <p style="color: var(--error-color);">Failed to load reasoning trace: ${error.message}</p>
            </div>
        `;
    }
}

function closeReasoningLedger() {
    document.getElementById('reasoning-ledger-modal').style.display = 'none';
}
