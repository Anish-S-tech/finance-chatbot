/* ═══════════════════════════════════════════════════════════════════════════
   FinanceAI — Main Application Logic
   ═══════════════════════════════════════════════════════════════════════════ */

const API = '';

// ── State ───────────────────────────────────────────────────────────────────
let conversations = [];
let activeConvId = null;
let isStreaming = false;
let currentModel = null;

// ── DOM refs ────────────────────────────────────────────────────────────────
const messagesEl = document.getElementById('messages');
const welcomeEl = document.getElementById('welcome');
const inputEl = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const chatListEl = document.getElementById('chat-list');
const chatTitle = document.getElementById('chat-title');
const newChatBtn = document.getElementById('new-chat-btn');
const sidebarEl = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebar-toggle');
const navTabs = document.querySelectorAll('.nav-tab');
const chatPanel = document.getElementById('chat-list-panel');
const toolsPanel = document.getElementById('tools-panel');
const toolBtns = document.querySelectorAll('.tool-btn');
const calcModal = document.getElementById('calc-modal');
const calcTitle = document.getElementById('calc-title');
const calcBody = document.getElementById('calc-body');
const calcResult = document.getElementById('calc-result');
const calcClose = document.getElementById('calc-close');
const quickPrompts = document.querySelectorAll('.quick-prompt');
const charCounter = document.getElementById('char-counter');
const modelBadge = document.getElementById('model-badge');
const modelNameDisplay = document.getElementById('model-name-display');
const statusDot = document.getElementById('status-dot');
const scrollBottomBtn = document.getElementById('scroll-bottom-btn');
const toastContainer = document.getElementById('toast-container');

// ── Init ────────────────────────────────────────────────────────────────────
loadConversations();
renderChatList();

// ── Toast System ────────────────────────────────────────────────────────────
function showToast(message, type = 'info', duration = 3000) {
    const icons = { success: '\u2713', error: '\u2717', info: '\u2022', warning: '!' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span class="toast-icon">${icons[type] || icons.info}</span><span>${message}</span>`;
    toastContainer.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('removing');
        toast.addEventListener('animationend', () => toast.remove());
    }, duration);
}

// ── Character Counter ───────────────────────────────────────────────────────
function updateCharCounter() {
    const len = inputEl.value.length;
    if (len > 0) {
        charCounter.textContent = `${len}/4000`;
        charCounter.classList.remove('warning', 'danger');
        if (len > 3500) charCounter.classList.add('danger');
        else if (len > 2800) charCounter.classList.add('warning');
    } else {
        charCounter.textContent = '';
    }
}

// ── Model Badge ─────────────────────────────────────────────────────────────
function updateModelBadge(modelId, isFallback = false) {
    if (!modelId) return;
    const shortName = modelId.split('/').pop().replace(/-instruct$/i, '');
    modelNameDisplay.textContent = shortName;
    modelBadge.classList.remove('active-model', 'fallback-model', 'error-model');
    modelBadge.classList.add(isFallback ? 'fallback-model' : 'active-model');
    currentModel = modelId;
}

function resetModelBadge() {
    modelNameDisplay.textContent = 'Ready';
    modelBadge.classList.remove('active-model', 'fallback-model', 'error-model');
}

// ── Relative Time ───────────────────────────────────────────────────────────
function relativeTime(date) {
    const diff = Date.now() - date;
    const s = Math.floor(diff / 1000);
    if (s < 10) return 'now';
    if (s < 60) return `${s}s`;
    const m = Math.floor(s / 60);
    if (m < 60) return `${m}m`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h`;
    return new Date(date).toLocaleDateString();
}

// ── Copy ────────────────────────────────────────────────────────────────────
async function copyToClipboard(text, btnEl) {
    try {
        await navigator.clipboard.writeText(text);
        if (btnEl) {
            btnEl.classList.add('copied');
            btnEl.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>';
            setTimeout(() => {
                btnEl.classList.remove('copied');
                btnEl.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
            }, 2000);
        }
        showToast('Copied to clipboard', 'success', 2000);
    } catch {
        showToast('Failed to copy', 'error', 2000);
    }
}

// ── Input handling ──────────────────────────────────────────────────────────
inputEl.addEventListener('input', () => {
    inputEl.style.height = 'auto';
    inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + 'px';
    sendBtn.disabled = !inputEl.value.trim() || isStreaming;
    updateCharCounter();
});

inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!sendBtn.disabled) sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);

document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        createNewConversation();
    }
});

quickPrompts.forEach(btn => {
    btn.addEventListener('click', () => {
        inputEl.value = btn.dataset.prompt;
        inputEl.dispatchEvent(new Event('input'));
        sendMessage();
    });
});

// ── Sidebar ─────────────────────────────────────────────────────────────────
sidebarToggle.addEventListener('click', () => sidebarEl.classList.toggle('collapsed'));
newChatBtn.addEventListener('click', () => createNewConversation());

navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        navTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        chatPanel.classList.toggle('active', tab.dataset.tab === 'chat');
        toolsPanel.classList.toggle('active', tab.dataset.tab === 'tools');
    });
});

// ── Scroll ──────────────────────────────────────────────────────────────────
messagesEl.addEventListener('scroll', () => {
    const nearBottom = messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight < 120;
    scrollBottomBtn.classList.toggle('hidden', nearBottom);
});
scrollBottomBtn.addEventListener('click', () => {
    scrollToBottom();
    scrollBottomBtn.classList.add('hidden');
});

// ── Chat logic ──────────────────────────────────────────────────────────────
function createNewConversation() {
    const conv = { id: Date.now().toString(), title: 'New Conversation', messages: [] };
    conversations.unshift(conv);
    activeConvId = conv.id;
    resetModelBadge();
    saveConversations();
    renderChatList();
    renderMessages();
}

function getActiveConv() {
    return conversations.find(c => c.id === activeConvId);
}

function deleteConversation(convId, event) {
    event.stopPropagation();
    conversations = conversations.filter(c => c.id !== convId);
    if (activeConvId === convId) {
        activeConvId = conversations.length > 0 ? conversations[0].id : null;
    }
    saveConversations();
    renderChatList();
    renderMessages();
}

async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text || isStreaming) return;
    if (!activeConvId) createNewConversation();

    const conv = getActiveConv();
    conv.messages.push({ role: 'user', content: text, timestamp: Date.now() });

    if (conv.title === 'New Conversation') {
        conv.title = text.length > 40 ? text.slice(0, 40) + '\u2026' : text;
    }

    inputEl.value = '';
    inputEl.style.height = 'auto';
    sendBtn.disabled = true;
    updateCharCounter();
    renderMessages();
    scrollToBottom();

    const typingRow = addTypingIndicator();
    isStreaming = true;

    try {
        const history = conv.messages.slice(0, -1).map(m => ({ role: m.role, content: m.content }));
        const response = await fetch(`${API}/api/chat/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, history }),
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantText = '';
        let buffer = '';
        let modelUsed = null;

        typingRow.remove();
        const { bubbleEl, footerEl } = addMessageBubble('assistant', '', Date.now(), null);

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                try {
                    const data = JSON.parse(line.slice(6));

                    if (data.model_used && !modelUsed) {
                        modelUsed = data.model_used;
                        updateModelBadge(modelUsed, false);
                        continue;
                    }

                    if (data.token) {
                        assistantText += data.token;
                        bubbleEl.innerHTML = renderMarkdown(assistantText);
                        scrollToBottom();
                    }

                    if (data.error) {
                        assistantText += `\n\nError: ${data.error}`;
                        bubbleEl.innerHTML = renderMarkdown(assistantText);
                        showToast(data.error, 'error', 5000);
                    }
                } catch (_) { }
            }
        }

        conv.messages.push({
            role: 'assistant',
            content: assistantText,
            timestamp: Date.now(),
            model: modelUsed || currentModel,
        });

        if (footerEl && modelUsed) {
            const shortName = modelUsed.split('/').pop().replace(/-instruct$/i, '');
            const copyBtnHtml = `<button class="msg-copy-btn" title="Copy"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></button>`;
            footerEl.innerHTML = `<span class="message-timestamp">${relativeTime(Date.now())}</span><span class="msg-model-tag">${shortName}</span>${copyBtnHtml}`;
            footerEl.style.opacity = '1';
            setTimeout(() => { footerEl.style.opacity = ''; }, 3000);
            const copyBtn = footerEl.querySelector('.msg-copy-btn');
            copyBtn.addEventListener('click', () => copyToClipboard(assistantText, copyBtn));
        }

        saveConversations();
        renderChatList();

    } catch (err) {
        typingRow.remove();
        const { bubbleEl } = addMessageBubble('assistant', '', Date.now(), null);
        bubbleEl.innerHTML = `<p>Failed to get a response. Please check that the backend is running.</p><p style="color:var(--text-dim);font-size:0.75rem">${err.message}</p>`;
        showToast('Connection failed', 'error', 4000);
        modelBadge.classList.add('error-model');
    } finally {
        isStreaming = false;
        sendBtn.disabled = !inputEl.value.trim();
    }
}

// ── Rendering ───────────────────────────────────────────────────────────────
function renderMessages() {
    const conv = getActiveConv();
    messagesEl.querySelectorAll('.message-row').forEach(el => el.remove());

    if (!conv || conv.messages.length === 0) {
        welcomeEl.style.display = 'flex';
        chatTitle.textContent = 'New Conversation';
        return;
    }

    welcomeEl.style.display = 'none';
    chatTitle.textContent = conv.title;
    conv.messages.forEach(msg => addMessageBubble(msg.role, msg.content, msg.timestamp, msg.model));
    scrollToBottom();
}

function addMessageBubble(role, content, timestamp, model) {
    const row = document.createElement('div');
    row.className = `message-row ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    // SVG icons instead of emojis
    if (role === 'assistant') {
        avatar.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>';
    } else {
        avatar.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>';
    }

    const bubbleWrap = document.createElement('div');
    bubbleWrap.style.cssText = 'display:flex;flex-direction:column;max-width:640px;';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = renderMarkdown(content);

    const footer = document.createElement('div');
    footer.className = 'message-footer';

    if (timestamp) {
        const timeEl = document.createElement('span');
        timeEl.className = 'message-timestamp';
        timeEl.textContent = relativeTime(timestamp);
        footer.appendChild(timeEl);
    }

    if (role === 'assistant' && model) {
        const modelTag = document.createElement('span');
        modelTag.className = 'msg-model-tag';
        modelTag.textContent = model.split('/').pop().replace(/-instruct$/i, '');
        footer.appendChild(modelTag);
    }

    if (role === 'assistant' && content) {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'msg-copy-btn';
        copyBtn.title = 'Copy';
        copyBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
        copyBtn.addEventListener('click', () => copyToClipboard(content, copyBtn));
        footer.appendChild(copyBtn);
    }

    bubbleWrap.appendChild(bubble);
    bubbleWrap.appendChild(footer);

    if (role === 'assistant') {
        row.appendChild(avatar);
        row.appendChild(bubbleWrap);
    } else {
        row.appendChild(bubbleWrap);
        row.appendChild(avatar);
    }

    messagesEl.appendChild(row);
    return { rowEl: row, bubbleEl: bubble, footerEl: footer };
}

function addTypingIndicator() {
    const row = document.createElement('div');
    row.className = 'message-row assistant';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = `
        <div class="typing-indicator">
            <div class="shimmer-line"></div>
            <div class="shimmer-line"></div>
            <div class="shimmer-line"></div>
        </div>
        <div class="typing-dots"><span></span><span></span><span></span></div>
    `;

    row.appendChild(avatar);
    row.appendChild(bubble);
    messagesEl.appendChild(row);
    scrollToBottom();
    return row;
}

function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderChatList() {
    chatListEl.innerHTML = '';
    conversations.forEach(conv => {
        const li = document.createElement('li');
        li.className = `chat-list-item${conv.id === activeConvId ? ' active' : ''}`;

        const title = document.createElement('span');
        title.textContent = conv.title;
        title.style.cssText = 'overflow:hidden;text-overflow:ellipsis;flex:1;';

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'chat-delete-btn';
        deleteBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
        deleteBtn.title = 'Delete';
        deleteBtn.addEventListener('click', (e) => deleteConversation(conv.id, e));

        li.appendChild(title);
        li.appendChild(deleteBtn);

        li.addEventListener('click', () => {
            activeConvId = conv.id;
            renderChatList();
            renderMessages();
            if (window.innerWidth <= 768) sidebarEl.classList.add('collapsed');
        });
        chatListEl.appendChild(li);
    });
}

// ── Markdown ────────────────────────────────────────────────────────────────
function renderMarkdown(text) {
    if (!text) return '';
    let html = escapeHtml(text);
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/^[-\u2022] (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
    html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    return `<p>${html}</p>`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ── Persistence ─────────────────────────────────────────────────────────────
function saveConversations() {
    localStorage.setItem('financeai_convos', JSON.stringify(conversations));
}

function loadConversations() {
    try {
        const data = localStorage.getItem('financeai_convos');
        if (data) {
            conversations = JSON.parse(data);
            if (conversations.length > 0) activeConvId = conversations[0].id;
        }
    } catch (_) {
        conversations = [];
    }
}

// ── Calculators ─────────────────────────────────────────────────────────────
const TOOL_CONFIG = {
    'compound-interest': {
        title: 'Compound Interest',
        fields: [
            { key: 'principal', label: 'Principal Amount', type: 'number', placeholder: '100000' },
            { key: 'rate', label: 'Annual Interest Rate (%)', type: 'number', placeholder: '8', step: '0.1' },
            { key: 'years', label: 'Number of Years', type: 'number', placeholder: '10' },
            { key: 'compounds_per_year', label: 'Compounds / Year', type: 'number', placeholder: '12' },
        ],
        endpoint: '/api/tools/compound-interest',
        formatResult: (r) => [
            { label: 'Future Value', value: `${num(r.future_value)}` },
            { label: 'Total Interest', value: `${num(r.total_interest)}` },
            { label: 'Effective Rate', value: `${r.effective_rate}%` },
            { label: 'Principal', value: `${num(r.principal)}` },
        ],
    },
    'emi': {
        title: 'EMI Calculator',
        fields: [
            { key: 'principal', label: 'Loan Amount', type: 'number', placeholder: '1000000' },
            { key: 'rate', label: 'Annual Interest Rate (%)', type: 'number', placeholder: '9', step: '0.1' },
            { key: 'tenure_months', label: 'Tenure (Months)', type: 'number', placeholder: '240' },
        ],
        endpoint: '/api/tools/emi',
        formatResult: (r) => [
            { label: 'Monthly EMI', value: `${num(r.emi)}` },
            { label: 'Total Payment', value: `${num(r.total_payment)}` },
            { label: 'Total Interest', value: `${num(r.total_interest)}` },
        ],
    },
    'sip': {
        title: 'SIP Returns',
        fields: [
            { key: 'monthly_investment', label: 'Monthly Investment', type: 'number', placeholder: '5000' },
            { key: 'rate', label: 'Expected Return (% p.a.)', type: 'number', placeholder: '12', step: '0.1' },
            { key: 'years', label: 'Investment Period (Years)', type: 'number', placeholder: '15' },
        ],
        endpoint: '/api/tools/sip',
        formatResult: (r) => [
            { label: 'Future Value', value: `${num(r.future_value)}` },
            { label: 'Total Invested', value: `${num(r.total_invested)}` },
            { label: 'Wealth Gained', value: `${num(r.wealth_gained)}` },
        ],
    },
    'inflation': {
        title: 'Inflation Impact',
        fields: [
            { key: 'amount', label: 'Current Amount', type: 'number', placeholder: '100000' },
            { key: 'rate', label: 'Inflation Rate (% p.a.)', type: 'number', placeholder: '6', step: '0.1' },
            { key: 'years', label: 'Years Into Future', type: 'number', placeholder: '10' },
        ],
        endpoint: '/api/tools/inflation',
        formatResult: (r) => [
            { label: 'Nominal Value', value: `${num(r.future_value)}` },
            { label: 'Real Purchasing Power', value: `${num(r.purchasing_power)}` },
            { label: 'Purchasing Power Loss', value: `${r.loss_percentage}%` },
        ],
    },
};

function num(n) {
    return Number(n).toLocaleString('en-IN', { maximumFractionDigits: 2 });
}

toolBtns.forEach(btn => {
    btn.addEventListener('click', () => openCalculator(btn.dataset.tool));
});

function openCalculator(toolKey) {
    const cfg = TOOL_CONFIG[toolKey];
    if (!cfg) return;

    calcTitle.textContent = cfg.title;
    calcResult.classList.add('hidden');
    calcResult.innerHTML = '';

    let formHtml = '';
    cfg.fields.forEach(f => {
        formHtml += `
      <div class="form-group">
        <label for="calc-${f.key}">${f.label}</label>
        <input id="calc-${f.key}" type="${f.type}" placeholder="${f.placeholder}" ${f.step ? `step="${f.step}"` : ''} />
      </div>`;
    });
    formHtml += `<button class="btn-calculate" id="calc-submit"><span class="calc-btn-text">Calculate</span></button>`;
    calcBody.innerHTML = formHtml;

    document.getElementById('calc-submit').addEventListener('click', async function () {
        const btn = this;
        const payload = {};
        let hasEmpty = false;

        for (const f of cfg.fields) {
            const input = document.getElementById(`calc-${f.key}`);
            const val = input.value;
            if (!val) {
                hasEmpty = true;
                input.style.borderColor = 'var(--error)';
                setTimeout(() => { input.style.borderColor = ''; }, 2000);
                continue;
            }
            payload[f.key] = Number(val);
        }

        if (hasEmpty) {
            showToast('Please fill in all fields', 'warning', 2500);
            return;
        }

        btn.classList.add('loading');
        btn.querySelector('.calc-btn-text').textContent = 'Calculating...';

        try {
            const res = await fetch(`${API}${cfg.endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!res.ok) throw new Error('Calculation failed');
            const data = await res.json();
            const items = cfg.formatResult(data);

            calcResult.innerHTML = items.map(i =>
                `<div class="result-item">
                    <span class="result-label">${i.label}</span>
                    <span class="result-value">${i.value}</span>
                </div>`
            ).join('');
            calcResult.classList.remove('hidden');
        } catch (err) {
            calcResult.innerHTML = `<div class="result-item"><span class="result-label" style="color:var(--error)">Error: ${err.message}</span></div>`;
            calcResult.classList.remove('hidden');
            showToast('Calculation failed', 'error', 3000);
        } finally {
            btn.classList.remove('loading');
            btn.querySelector('.calc-btn-text').textContent = 'Calculate';
        }
    });

    calcModal.classList.remove('hidden');
}

calcClose.addEventListener('click', () => calcModal.classList.add('hidden'));
calcModal.addEventListener('click', (e) => {
    if (e.target === calcModal) calcModal.classList.add('hidden');
});
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') calcModal.classList.add('hidden');
});
