/**
 * Local File Manager Agent - Frontend JavaScript
 * Handles chat UI, API communication, and user interactions
 */

// Configuration
const CONFIG = {
    API_BASE_URL: 'http://localhost:5001',
    TYPING_DELAY: 1000, // ms
    SCROLL_BEHAVIOR: 'smooth'
};

// DOM Elements
const chatContainer = document.getElementById('chatContainer');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const typingIndicator = document.getElementById('typingIndicator');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');

// State
let isProcessing = false;

/**
 * Initialize the application
 */
async function init() {
    console.log('🚀 Initializing File Manager Agent...');

    // Check API health
    await checkAPIHealth();

    // Setup event listeners
    setupEventListeners();

    // Setup example click handlers
    setupExampleHandlers();

    console.log('✅ Application ready');
}

/**
 * Check if backend API is available
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            updateStatus(true, 'Connected');
            console.log('✅ API connected:', data);
        } else {
            updateStatus(false, 'API Error');
        }
    } catch (error) {
        console.error('❌ API connection failed:', error);
        updateStatus(false, 'Disconnected');

        // Show error message in chat
        addAgentMessage(
            'Unable to connect to the backend server. Please make sure the Flask server is running on http://localhost:5000',
            'error'
        );
    }
}

/**
 * Update connection status indicator
 */
function updateStatus(isConnected, text) {
    if (isConnected) {
        statusDot.classList.add('connected');
    } else {
        statusDot.classList.remove('connected');
    }
    statusText.textContent = text;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Form submit
    chatForm.addEventListener('submit', handleFormSubmit);

    // Enter key to send (Shift+Enter for new line)
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleFormSubmit(e);
        }
    });
}

/**
 * Setup click handlers for example queries
 */
function setupExampleHandlers() {
    const examples = document.querySelectorAll('.examples li');
    examples.forEach(example => {
        example.addEventListener('click', () => {
            const text = example.textContent.replace('💡 ', '').trim();
            messageInput.value = text;
            messageInput.focus();
        });
    });
}

/**
 * Handle form submission
 */
async function handleFormSubmit(e) {
    e.preventDefault();

    if (isProcessing) return;

    const message = messageInput.value.trim();
    if (!message) return;

    // Clear input
    messageInput.value = '';
    messageInput.focus();

    // Add user message to chat
    addUserMessage(message);

    // Process the message
    await processMessage(message);
}

/**
 * Process user message and get response
 */
async function processMessage(message) {
    isProcessing = true;
    showTypingIndicator();

    try {
        // First, send to chat endpoint to get action
        const chatResponse = await fetch(`${CONFIG.API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                context: {}
            })
        });

        const chatData = await chatResponse.json();

        if (chatData.error) {
            throw new Error(chatData.error);
        }

        // If it's a help response, show it
        if (chatData.action === 'help') {
            hideTypingIndicator();
            addAgentMessage(chatData.response);
            isProcessing = false;
            return;
        }

        // Execute the action
        if (chatData.action_info) {
            const executeResponse = await fetch(`${CONFIG.API_BASE_URL}/api/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(chatData.action_info)
            });

            const executeData = await executeResponse.json();

            hideTypingIndicator();

            if (executeData.success) {
                addAgentMessage(
                    formatResponse(executeData, chatData.action_info.action),
                    'success'
                );
            } else {
                throw new Error(executeData.error || 'Operation failed');
            }
        }

    } catch (error) {
        console.error('❌ Error processing message:', error);
        hideTypingIndicator();
        addAgentMessage(
            `Sorry, I encountered an error: ${error.message}`,
            'error'
        );
    } finally {
        isProcessing = false;
    }
}

/**
 * Format response based on action type
 */
function formatResponse(data, action) {
    let html = `<p>${data.message}</p>`;

    if (action === 'find_by_extension' && data.data && data.data.length > 0) {
        html += formatFileList(data.data);
    } else if (action === 'largest_files' && data.data && data.data.length > 0) {
        html += formatFileList(data.data);
    } else if (action === 'list_directory' && data.data) {
        html += formatDirectoryList(data.data);
    } else if (action === 'create_folder' && data.data) {
        html += `<p class="file-path">📁 ${data.data.path}</p>`;
    } else if (action === 'find_duplicates' && data.data && data.data.duplicate_groups) {
        html += formatDuplicateGroups(data.data);
    }

    return html;
}

/**
 * Format file list as table
 */
function formatFileList(files) {
    let html = '<div class="file-results"><table class="file-table">';
    html += '<thead><tr><th>Name</th><th>Size</th><th>Modified</th></tr></thead>';
    html += '<tbody>';

    files.forEach(file => {
        const modified = new Date(file.modified).toLocaleString();
        html += `
            <tr>
                <td><span class="file-path">${escapeHtml(file.name)}</span></td>
                <td>${file.readable_size}</td>
                <td>${modified}</td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';
    return html;
}

/**
 * Format directory listing
 */
function formatDirectoryList(dirData) {
    let html = `<p class="file-path">📂 ${escapeHtml(dirData.directory)}</p>`;
    html += '<div class="file-results"><table class="file-table">';
    html += '<thead><tr><th>Name</th><th>Type</th><th>Size</th></tr></thead>';
    html += '<tbody>';

    dirData.items.forEach(item => {
        const icon = item.is_directory ? '📁' : '📄';
        const type = item.is_directory ? 'Directory' : 'File';
        html += `
            <tr>
                <td>${icon} <span class="file-path">${escapeHtml(item.name)}</span></td>
                <td>${type}</td>
                <td>${item.readable_size}</td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';
    return html;
}

/**
 * Format duplicate file groups
 */
function formatDuplicateGroups(duplicateData) {
    const groups = duplicateData.duplicate_groups || [];

    if (groups.length === 0) {
        return '<p>No duplicate files found.</p>';
    }

    // Show first 10 groups to avoid overwhelming the UI
    const displayGroups = groups.slice(0, 10);
    const hasMore = groups.length > 10;

    let html = '<div class="file-results" style="margin-top: 15px;">';

    displayGroups.forEach((group, index) => {
        html += `
            <div style="margin-bottom: 20px; padding: 15px; background: rgba(102, 126, 234, 0.1); border-radius: 8px; border-left: 4px solid #667eea;">
                <h4 style="margin: 0 0 10px 0; color: #667eea;">
                    Group ${index + 1}
                    <span style="color: #f56565; font-weight: bold;">(${group.wasted_readable} wasted)</span>
                </h4>
        `;

        // List all files in this group
        group.files.forEach((file, fileIndex) => {
            html += `
                <div style="margin: 5px 0; padding: 8px; background: rgba(0, 0, 0, 0.2); border-radius: 4px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="file-path" style="flex: 1; word-break: break-all;">
                            📄 ${escapeHtml(file.path)}
                        </span>
                        <span style="margin-left: 15px; white-space: nowrap; color: #a0aec0;">
                            ${file.readable_size}
                        </span>
                    </div>
                </div>
            `;
        });

        html += '</div>';
    });

    if (hasMore) {
        html += `
            <p style="color: #a0aec0; font-style: italic;">
                ... and ${groups.length - 10} more duplicate group(s).
                Showing first 10 groups only.
            </p>
        `;
    }

    html += '</div>';
    return html;
}

/**
 * Add user message to chat
 */
function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="avatar user-avatar">👤</div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
        </div>
    `;

    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Add agent message to chat
 */
function addAgentMessage(html, type = 'normal') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message agent-message ${type}-message`;
    messageDiv.innerHTML = `
        <div class="avatar agent-avatar">🤖</div>
        <div class="message-content">
            <div class="message-text">${html}</div>
        </div>
    `;

    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    scrollToBottom();
}

/**
 * Hide typing indicator
 */
function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

/**
 * Scroll chat to bottom
 */
function scrollToBottom() {
    setTimeout(() => {
        chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: CONFIG.SCROLL_BEHAVIOR
        });
    }, 100);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
