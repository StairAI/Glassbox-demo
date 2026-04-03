// Glass Box Explorer - Main JavaScript

const API_BASE = 'http://localhost:8080/api';

// State
let currentTab = 'triggers';
let triggers = [];
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
            loadTriggers();
        });
    }

    // Initial load
    loadOwners();
    loadTriggers();
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
// Triggers Tab
// ============================================================================

async function loadTriggers() {
    try {
        const params = new URLSearchParams();
        if (selectedOwner && selectedOwner !== 'all') {
            params.append('owner', selectedOwner);
        }

        const url = `${API_BASE}/triggers${params.toString() ? '?' + params.toString() : ''}`;
        const response = await fetch(url);
        const data = await response.json();

        triggers = data.triggers || [];
        updateTriggerStats(triggers);
        renderTriggers(triggers);
    } catch (error) {
        console.error('Error loading triggers:', error);
        document.getElementById('triggers-list').innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <p>Error loading triggers from SUI network</p>
                <p style="font-size: 12px; margin-top: 10px;">${error.message}</p>
            </div>
        `;
    }
}

function updateTriggerStats(triggersData) {
    const newsCount = triggersData.filter(t => t.trigger_type === 'news').length;
    const signalCount = triggersData.filter(t => t.trigger_type === 'signal').length;

    // Get latest timestamp
    const timestamps = triggersData.map(t => new Date(t.timestamp));
    const latest = timestamps.length > 0 ? new Date(Math.max(...timestamps)) : null;

    document.getElementById('total-triggers').textContent = triggersData.length;
    document.getElementById('news-triggers').textContent = newsCount;
    document.getElementById('signal-triggers').textContent = signalCount;
    document.getElementById('latest-update').textContent = latest
        ? formatTimeAgo(latest)
        : 'N/A';
}

function renderTriggers(triggersToRender) {
    const container = document.getElementById('triggers-list');

    if (triggersToRender.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <p>No triggers found on SUI network</p>
            </div>
        `;
        return;
    }

    // Pagination
    const totalPages = Math.ceil(triggersToRender.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedTriggers = triggersToRender.slice(startIndex, endIndex);

    // Render triggers
    const triggersHTML = paginatedTriggers.map(trigger => {
        return createTriggerCard(trigger);
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
                Page ${currentPage} of ${totalPages} (${triggersToRender.length} total items)
            </span>
            <button
                onclick="changePage(${currentPage + 1})"
                ${currentPage === totalPages ? 'disabled' : ''}
                style="padding: 8px 16px; background: ${currentPage === totalPages ? '#333' : '#4CAF50'}; color: white; border: none; border-radius: 4px; cursor: ${currentPage === totalPages ? 'not-allowed' : 'pointer'};">
                Next →
            </button>
        </div>
    ` : '';

    container.innerHTML = triggersHTML + paginationHTML;
}

function changePage(newPage) {
    currentPage = newPage;
    filterTriggers();
}

function createTriggerCard(trigger) {
    const typeClass = trigger.trigger_type === 'news' ? 'news' : 'signal';

    return `
        <div class="trigger-card" data-trigger-id="${trigger.trigger_id || 'unknown'}">
            <div class="trigger-header">
                <span class="trigger-type ${typeClass}">${trigger.trigger_type}</span>
                <span class="trigger-timestamp">${formatTimestamp(trigger.timestamp)}</span>
            </div>
            <div class="trigger-body">
                <div class="trigger-field">
                    <div class="field-label">Trigger ID</div>
                    <div class="field-value">${trigger.trigger_id || 'N/A'}</div>
                </div>
                <div class="trigger-field">
                    <div class="field-label">SUI Object ID</div>
                    <div class="field-value">${truncate(trigger.object_id || 'N/A', 32)}</div>
                </div>
                <div class="trigger-field">
                    <div class="field-label">Walrus Blob ID</div>
                    <div class="field-value">${truncate(trigger.walrus_blob_id || 'N/A', 32)}</div>
                </div>
                <div class="trigger-field">
                    <div class="field-label">Owner</div>
                    <div class="field-value">${truncate(trigger.owner || 'default', 32)}</div>
                </div>
                <div class="trigger-field">
                    <div class="field-label">Producer</div>
                    <div class="field-value">${trigger.producer || 'N/A'}</div>
                </div>
                <div class="trigger-field">
                    <div class="field-label">Size</div>
                    <div class="field-value">${formatBytes(trigger.size_bytes || 0)}</div>
                </div>
            </div>
            ${trigger.walrus_blob_id ? `
                <div style="margin-top: 12px;">
                    <a href="https://walruscan.com/testnet/blob/${trigger.walrus_blob_id}"
                       target="_blank"
                       class="expand-btn"
                       style="text-decoration: none; display: block; text-align: center; padding: 10px;"
                       title="View on Walruscan explorer">
                        🔗 View on Walruscan
                    </a>
                </div>
            ` : ''}
        </div>
    `;
}

async function viewWalrusData(triggerId) {
    try {
        showToast('Fetching full data from Walrus...', 'info', 'Loading');

        const response = await fetch(`${API_BASE}/triggers/${triggerId}/full`);
        const data = await response.json();

        if (!data.success) {
            showToast(data.error || 'Failed to fetch trigger data', 'error', 'Fetch Failed');
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

function refreshTriggers() {
    document.getElementById('triggers-list').innerHTML = '<div class="loading">Refreshing...</div>';
    loadTriggers();
}

// Filter triggers
document.getElementById('trigger-type-filter')?.addEventListener('change', (e) => {
    currentPage = 1;  // Reset to first page
    filterTriggers();
});

document.getElementById('search-box')?.addEventListener('input', (e) => {
    currentPage = 1;  // Reset to first page
    filterTriggers();
});

function filterTriggers() {
    const typeFilter = document.getElementById('trigger-type-filter').value;
    const searchQuery = document.getElementById('search-box').value.toLowerCase();

    let filtered = triggers;

    // Filter by type
    if (typeFilter !== 'all') {
        filtered = filtered.filter(t => t.trigger_type === typeFilter);
    }

    // Filter by search
    if (searchQuery) {
        filtered = filtered.filter(t => {
            const searchText = `
                ${t.trigger_id}
                ${t.object_id}
                ${t.producer}
                ${t.signal_type || ''}
            `.toLowerCase();
            return searchText.includes(searchQuery);
        });
    }

    renderTriggers(filtered);
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
            <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 15px;">
                ${formatTimestamp(trace.timestamp)}
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
                    <div><strong>Trigger ID:</strong> ${metadata.trigger_id || 'N/A'}</div>
                    <div><strong>Type:</strong> ${metadata.trigger_type || 'N/A'}</div>
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

    if (event.target === agentModal) {
        closeAgentDetail();
    }
    if (event.target === walrusModal) {
        closeWalrusDataModal();
    }
}
