const API_BASE_URL = "http://127.0.0.1:8000";

const sourceLangSelect = document.getElementById("source-lang");
const targetLangSelect = document.getElementById("target-lang");
const swapBtn = document.getElementById("swap-langs-btn");
const sourceTextArea = document.getElementById("source-text");
const translatedTextArea = document.getElementById("translated-text");
const charCount = document.getElementById("char-count");
const targetLangTab = document.getElementById("target-lang-tab");
const form = document.getElementById("translator-form");
const translateBtn = document.getElementById("translate-btn");
const errorMessage = document.getElementById("error-message");
const statusMessage = document.getElementById("status-message");

const MAX_CHARS = 5000;
const DEFAULT_TARGET = "en";

/** Announce a message to assistive tech via the polite live region. */
function announce(message) {
  statusMessage.textContent = message;
}

/** Show a visible + announced error. Pass null/empty to clear it. */
function showError(message) {
  if (!message) {
    errorMessage.textContent = "";
    errorMessage.classList.add("hidden");
    return;
  }
  errorMessage.textContent = message;
  errorMessage.classList.remove("hidden");
  announce(message);
}

/** Populate a <select> with {code: name} entries. */
function populateSelect(selectEl, languages, { skipAuto = false } = {}) {
  selectEl.innerHTML = "";
  for (const [code, name] of Object.entries(languages)) {
    if (skipAuto && code === "auto") continue;
    const option = document.createElement("option");
    option.value = code;
    option.textContent = name;
    selectEl.appendChild(option);
  }
}

function updateCharCount() {
  const length = sourceTextArea.value.length;
  charCount.textContent = `${length} / ${MAX_CHARS}`;
}

function updateTargetLangTab() {
  const code = targetLangSelect.value || "";
  targetLangTab.textContent = code.slice(0, 2).toUpperCase();
}

function updateSwapButtonState() {
  swapBtn.disabled = sourceLangSelect.value === "auto";
}

async function loadLanguages() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/languages`);
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }
    const data = await response.json();

    populateSelect(sourceLangSelect, data.languages);
    populateSelect(targetLangSelect, data.languages, { skipAuto: true });

    sourceLangSelect.value = "auto";
    targetLangSelect.value =
      DEFAULT_TARGET in data.languages ? DEFAULT_TARGET : targetLangSelect.options[0]?.value ?? "";

    updateTargetLangTab();
    updateSwapButtonState();
  } catch (error) {
    showError("Could not load the list of languages. Please refresh the page.");
    console.error("Failed to load languages:", error);
  }
}

function swapLanguages() {
  if (sourceLangSelect.value === "auto") return;

  const sourceValue = sourceLangSelect.value;
  const targetValue = targetLangSelect.value;

  // Only swap if the target select actually has the source language as an option.
  if ([...targetLangSelect.options].some((opt) => opt.value === sourceValue)) {
    targetLangSelect.value = sourceValue;
  }
  if ([...sourceLangSelect.options].some((opt) => opt.value === targetValue)) {
    sourceLangSelect.value = targetValue;
  }

  const sourceText = sourceTextArea.value;
  const translatedText = translatedTextArea.value;
  sourceTextArea.value = translatedText;
  translatedTextArea.value = sourceText;

  updateCharCount();
  updateTargetLangTab();
  updateSwapButtonState();
}

function setLoading(isLoading) {
  translateBtn.disabled = isLoading;
  translateBtn.querySelector(".btn-label").textContent = isLoading ? "Translating…" : "Translate";
}

async function handleSubmit(event) {
  event.preventDefault();

  const text = sourceTextArea.value;
  if (!text.trim()) {
    showError("Please enter some text to translate.");
    sourceTextArea.focus();
    return;
  }

  showError(null);
  setLoading(true);
  announce("Translating…");

  try {
    const response = await fetch(`${API_BASE_URL}/api/translate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        source_lang: sourceLangSelect.value,
        target_lang: targetLangSelect.value,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      const message = data?.detail || "Translation failed. Please try again.";
      throw new Error(message);
    }

    translatedTextArea.value = data.translated_text;
    announce("Translation complete.");
  } catch (error) {
    showError(error.message || "Something went wrong. Please check your connection and try again.");
    console.error("Translation request failed:", error);
  } finally {
    setLoading(false);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadLanguages();
  updateCharCount();
});

sourceTextArea.addEventListener("input", updateCharCount);
sourceLangSelect.addEventListener("change", updateSwapButtonState);
targetLangSelect.addEventListener("change", updateTargetLangTab);
swapBtn.addEventListener("click", swapLanguages);
form.addEventListener("submit", handleSubmit);