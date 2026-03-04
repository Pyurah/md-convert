/**
 * Markdown to Google Docs Converter - Frontend Application
 *
 * Handles live preview, clipboard copy via server API, file upload,
 * and editor interactions.
 */

// ---------------------------------------------------------------------------
// DOM References
// ---------------------------------------------------------------------------

const markdownInput = document.getElementById("markdown-input");
const previewRich = document.getElementById("preview-rich");
const previewHtml = document.getElementById("preview-html");
const btnCopy = document.getElementById("btn-copy");
const btnClear = document.getElementById("btn-clear");
const btnShutdown = document.getElementById("btn-shutdown");
const fileInput = document.getElementById("file-input");
const btnPreviewRich = document.getElementById("btn-preview-rich");
const btnPreviewHtml = document.getElementById("btn-preview-html");
const statusText = document.getElementById("status");
const charCount = document.getElementById("char-count");
const lineCount = document.getElementById("line-count");
const wordCount = document.getElementById("word-count");
const toast = document.getElementById("toast");
const toastMessage = document.getElementById("toast-message");

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

let debounceTimer = null;
let lastServerHtml = "";
let isRichPreview = true;

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    // Set up marked.js options for client-side preview
    marked.setOptions({
        gfm: true,
        breaks: true,
        tables: true,
    });

    // Bind events
    markdownInput.addEventListener("input", onInputChange);
    markdownInput.addEventListener("keydown", onKeyDown);
    btnCopy.addEventListener("click", onCopyClick);
    btnClear.addEventListener("click", onClearClick);
    btnShutdown.addEventListener("click", onShutdownClick);
    fileInput.addEventListener("change", onFileSelect);
    btnPreviewRich.addEventListener("click", () => togglePreview(true));
    btnPreviewHtml.addEventListener("click", () => togglePreview(false));

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
        // Ctrl+Shift+C = Copy to clipboard
        if (e.ctrlKey && e.shiftKey && e.key === "C") {
            e.preventDefault();
            onCopyClick();
        }
    });

    // Initial stats update
    updateStats();
});

// ---------------------------------------------------------------------------
// Live Preview (Client-Side with marked.js)
// ---------------------------------------------------------------------------

function onInputChange() {
    // Update stats immediately
    updateStats();

    // Debounced live preview
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        renderPreview();
    }, 300);
}

function renderPreview() {
    const md = markdownInput.value;

    if (!md.trim()) {
        previewRich.innerHTML =
            '<div class="preview-placeholder"><p>Your formatted preview will appear here as you type...</p></div>';
        previewHtml.textContent = "";
        lastServerHtml = "";
        return;
    }

    // Client-side preview with marked.js (instant)
    try {
        const html = marked.parse(md);
        previewRich.innerHTML = html;
        setStatus("Preview updated");
    } catch (err) {
        console.error("Preview error:", err);
        setStatus("Preview error");
    }

    // Also fetch server-side HTML for accurate Google Docs representation
    fetchServerHtml(md);
}

async function fetchServerHtml(md) {
    try {
        const response = await fetch("/api/convert", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ markdown: md }),
        });

        if (response.ok) {
            const data = await response.json();
            lastServerHtml = data.html;

            // Update HTML source view if active
            if (!isRichPreview) {
                previewHtml.textContent = formatHtml(lastServerHtml);
            }
        }
    } catch (err) {
        console.error("Server conversion error:", err);
    }
}

// ---------------------------------------------------------------------------
// Copy to Clipboard
// ---------------------------------------------------------------------------

async function onCopyClick() {
    const md = markdownInput.value;

    if (!md.trim()) {
        showToast("Nothing to copy — enter some Markdown first!", "warning");
        return;
    }

    setStatus("Copying to clipboard...");
    btnCopy.disabled = true;
    btnCopy.classList.add("loading");

    try {
        const response = await fetch("/api/clipboard", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ markdown: md }),
        });

        const data = await response.json();

        if (data.success) {
            showToast("✅ Copied! Paste into Google Docs with Ctrl+V", "success");
            setStatus("Copied to clipboard!");
        } else {
            showToast(`❌ ${data.message}`, "error");
            setStatus("Copy failed");
        }
    } catch (err) {
        showToast(`❌ Error: ${err.message}`, "error");
        setStatus("Copy failed");
    } finally {
        btnCopy.disabled = false;
        btnCopy.classList.remove("loading");
    }
}

// ---------------------------------------------------------------------------
// Clear Editor
// ---------------------------------------------------------------------------

function onClearClick() {
    if (markdownInput.value.trim() && !confirm("Clear all content?")) {
        return;
    }

    markdownInput.value = "";
    previewRich.innerHTML =
        '<div class="preview-placeholder"><p>Your formatted preview will appear here as you type...</p></div>';
    previewHtml.textContent = "";
    lastServerHtml = "";
    updateStats();
    setStatus("Cleared");
    markdownInput.focus();
}

// ---------------------------------------------------------------------------
// Stop Server
// ---------------------------------------------------------------------------

async function onShutdownClick() {
    if (!confirm("Stop the MD Converter server? You can restart it by double-clicking 'Start MD Converter.vbs'.")) {
        return;
    }

    try {
        await fetch("/api/shutdown", { method: "POST" });
        document.body.innerHTML =
            '<div style="display:flex;align-items:center;justify-content:center;height:100vh;background:#1e1e2e;color:#e0e0f0;font-family:Segoe UI,Arial,sans-serif;flex-direction:column;gap:16px;">' +
            '<h1 style="font-size:24px;">⏹️ Server Stopped</h1>' +
            '<p style="color:#a0a0c0;">You can close this tab. To restart, double-click <strong>Start MD Converter.vbs</strong></p>' +
            '</div>';
    } catch (err) {
        // Connection error is expected since server is shutting down
        document.body.innerHTML =
            '<div style="display:flex;align-items:center;justify-content:center;height:100vh;background:#1e1e2e;color:#e0e0f0;font-family:Segoe UI,Arial,sans-serif;flex-direction:column;gap:16px;">' +
            '<h1 style="font-size:24px;">⏹️ Server Stopped</h1>' +
            '<p style="color:#a0a0c0;">You can close this tab. To restart, double-click <strong>Start MD Converter.vbs</strong></p>' +
            '</div>';
    }
}

// ---------------------------------------------------------------------------
// File Upload
// ---------------------------------------------------------------------------

function onFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        markdownInput.value = e.target.result;
        updateStats();
        renderPreview();
        showToast(`📂 Loaded: ${file.name}`, "success");
        setStatus(`Loaded ${file.name}`);
    };
    reader.onerror = () => {
        showToast("❌ Failed to read file", "error");
    };
    reader.readAsText(file);

    // Reset input so same file can be loaded again
    event.target.value = "";
}

// ---------------------------------------------------------------------------
// Preview Toggle (Rich vs. HTML Source)
// ---------------------------------------------------------------------------

function togglePreview(rich) {
    isRichPreview = rich;

    if (rich) {
        previewRich.hidden = false;
        previewHtml.hidden = true;
        btnPreviewRich.classList.add("active");
        btnPreviewHtml.classList.remove("active");
    } else {
        previewRich.hidden = true;
        previewHtml.hidden = false;
        btnPreviewRich.classList.remove("active");
        btnPreviewHtml.classList.add("active");

        // Show server HTML if available
        if (lastServerHtml) {
            previewHtml.textContent = formatHtml(lastServerHtml);
        } else {
            previewHtml.textContent = "(Convert some markdown to see the HTML output)";
        }
    }
}

// ---------------------------------------------------------------------------
// Keyboard Handling
// ---------------------------------------------------------------------------

function onKeyDown(event) {
    // Tab key inserts spaces instead of moving focus
    if (event.key === "Tab") {
        event.preventDefault();
        const start = markdownInput.selectionStart;
        const end = markdownInput.selectionEnd;
        const value = markdownInput.value;

        markdownInput.value = value.substring(0, start) + "    " + value.substring(end);
        markdownInput.selectionStart = markdownInput.selectionEnd = start + 4;

        // Trigger input event for preview update
        markdownInput.dispatchEvent(new Event("input"));
    }
}

// ---------------------------------------------------------------------------
// Utility Functions
// ---------------------------------------------------------------------------

function updateStats() {
    const text = markdownInput.value;
    const chars = text.length;
    const lines = text ? text.split("\n").length : 0;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;

    charCount.textContent = `${chars} character${chars !== 1 ? "s" : ""}`;
    lineCount.textContent = `${lines} line${lines !== 1 ? "s" : ""}`;
    wordCount.textContent = `${words} word${words !== 1 ? "s" : ""}`;
}

function setStatus(message) {
    statusText.textContent = message;
}

function showToast(message, type = "info") {
    toastMessage.textContent = message;
    toast.className = `toast toast-${type}`;
    toast.hidden = false;

    // Auto-hide after 3 seconds
    setTimeout(() => {
        toast.hidden = true;
    }, 3000);
}

function formatHtml(html) {
    // Simple HTML formatting for display
    return html
        .replace(/></g, ">\n<")
        .replace(/\n\n+/g, "\n");
}
