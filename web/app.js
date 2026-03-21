const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

let sessionId = null;

const numRotorsInput = document.getElementById("numRotors");
const seedInput = document.getElementById("seed");
const randomizePositionsInput = document.getElementById("randomizePositions");
const animationDelayInput = document.getElementById("animationDelay");
const animationDelayValue = document.getElementById("animationDelayValue");
const startSessionBtn = document.getElementById("startSession");
const rotorStrip = document.getElementById("rotorStrip");
const reflectorDisplay = document.getElementById("reflectorDisplay");
const keyboard = document.getElementById("keyboard");
const lastInput = document.getElementById("lastInput");
const lastOutput = document.getElementById("lastOutput");
const currentTraceValue = document.getElementById("currentTraceValue");
const timeline = document.getElementById("timeline");
const messageInput = document.getElementById("messageInput");
const cipherOutput = document.getElementById("cipherOutput");
const encryptMessageBtn = document.getElementById("encryptMessage");
const clearMessageBtn = document.getElementById("clearMessage");
const copyCipherToInputBtn = document.getElementById("copyCipherToInput");
const plugboard = document.getElementById("plugboard");
const sessionGatedPanels = document.querySelectorAll(".session-gated");

let highlightDelayMs = 500;
let isBusy = false;

function setTimelineText(text) {
  timeline.textContent = text;
}

function syncResetButtonState() {
  const resetButton = document.getElementById("resetRotorsInline");
  if (resetButton) {
    resetButton.disabled = isBusy || !sessionId;
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function updateAnimationDelay() {
  const seconds = Math.max(0, Number(animationDelayInput.value || 0));
  highlightDelayMs = seconds * 1000;
  animationDelayValue.textContent = seconds.toFixed(2);
}

function getPairKey(letter1, letter2) {
  return [letter1, letter2].sort().join("|");
}

function setSessionEnabled(enabled) {
  sessionGatedPanels.forEach((panel) => {
    panel.classList.toggle("disabled", !enabled);
  });
  encryptMessageBtn.disabled = !enabled;
  clearMessageBtn.disabled = !enabled;
  copyCipherToInputBtn.disabled = !enabled;
  messageInput.disabled = !enabled;
  syncResetButtonState();
}

function setBusyState(busy) {
  isBusy = busy;
  startSessionBtn.disabled = busy;
  numRotorsInput.disabled = busy;
  seedInput.disabled = busy;
  encryptMessageBtn.disabled = busy || !sessionId;
  clearMessageBtn.disabled = busy || !sessionId;
  copyCipherToInputBtn.disabled = busy || !sessionId;
  messageInput.disabled = busy || !sessionId;
  syncResetButtonState();
}

function appendTypedPair(inputLetter, outputLetter) {
  messageInput.value += inputLetter;
  cipherOutput.value += outputLetter;
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Request failed");
  }
  return response.json();
}

function renderKeyboard() {
  keyboard.innerHTML = "";
  alphabet.forEach((letter) => {
    const btn = document.createElement("button");
    btn.className = "key";
    btn.textContent = letter;
    btn.dataset.letter = letter;
    btn.addEventListener("click", async () => {
      if (!sessionId || isBusy) {
        setTimelineText("Start a session first.");
        return;
      }
      await encryptKey(letter);
    });
    keyboard.appendChild(btn);
  });
}

function renderState(state) {
  reflectorDisplay.innerHTML = "";
  const seenReflectorLetters = new Set();
  Object.keys(state.reflector.mappings)
    .sort()
    .forEach((letter) => {
      if (seenReflectorLetters.has(letter)) {
        return;
      }
      const mapped = state.reflector.mappings[letter];
      seenReflectorLetters.add(letter);
      seenReflectorLetters.add(mapped);

      const pair = document.createElement("div");
      pair.className = "reflector-pair";
      pair.dataset.pairKey = getPairKey(letter, mapped);
      pair.textContent = `${letter} ↔ ${mapped}`;
      reflectorDisplay.appendChild(pair);
    });

  rotorStrip.innerHTML = "";
  state.rotors.forEach((rotor) => {
    const positionLetter = String.fromCharCode(65 + (rotor.position % 26));
    const wiringSample = rotor.mappings?.A ?? "-";
    const el = document.createElement("div");
    el.className = "rotor";
    el.dataset.rotorIndex = String(rotor.index);
    el.innerHTML = `<strong>Rotor ${rotor.index}</strong><div>Letter: ${positionLetter}</div><div>Position: ${rotor.position}</div><div>Wiring: A→${wiringSample}</div>`;
    rotorStrip.appendChild(el);
  });

  const resetButton = document.createElement("button");
  resetButton.id = "resetRotorsInline";
  resetButton.type = "button";
  resetButton.className = "rotor-reset-btn";
  resetButton.textContent = "Reset";
  resetButton.disabled = isBusy || !sessionId;
  resetButton.addEventListener("click", async () => {
    try {
      await resetRotors();
    } catch (error) {
      setBusyState(false);
      setTimelineText(`Error: ${error.message}`);
    }
  });
  rotorStrip.appendChild(resetButton);

  plugboard.innerHTML = "";
  const seenPlugboardLetters = new Set();
  Object.keys(state.plugboard.mappings)
    .sort()
    .forEach((letter) => {
      if (seenPlugboardLetters.has(letter)) {
        return;
      }

      const mapped = state.plugboard.mappings[letter];
      seenPlugboardLetters.add(letter);
      seenPlugboardLetters.add(mapped);

      const cell = document.createElement("div");
      cell.className = "mapping-cell";
      cell.dataset.pairKey = getPairKey(letter, mapped);
      cell.textContent = `${letter} ↔ ${mapped}`;
      plugboard.appendChild(cell);
    });
}

function clearKeyHighlights() {
  document.querySelectorAll(".key.input-active, .key.output-active").forEach((element) => {
    element.classList.remove("input-active", "output-active");
  });
}

function clearComponentHighlights() {
  document
    .querySelectorAll(".mapping-cell.component-active, .reflector-pair.component-active, .rotor.component-active")
    .forEach((element) => {
      element.classList.remove("component-active");
    });
}

function activateKey(letter, className) {
  const keyEl = document.querySelector(`.key[data-letter="${letter}"]`);
  if (keyEl) {
    keyEl.classList.add(className);
  }
}

function setCurrentTraceValue(value) {
  currentTraceValue.textContent = value;
}

async function animateKeySequence(inputLetter, outputLetter) {
  clearComponentHighlights();
  clearKeyHighlights();
  activateKey(inputLetter, "input-active");
  setCurrentTraceValue(inputLetter);
  await sleep(highlightDelayMs);
  activateKey(outputLetter, "output-active");
  setCurrentTraceValue(outputLetter);
  await sleep(highlightDelayMs);
  clearComponentHighlights();
  clearKeyHighlights();
}

function highlightTraceStep(step) {
  if (step.component === "rotor") {
    const rotor = rotorStrip.querySelector(`.rotor[data-rotor-index="${step.index}"]`);
    if (rotor) {
      rotor.classList.add("component-active");
    }
    return;
  }

  const pairKey = getPairKey(step.from, step.to);
  if (step.component === "plugboard") {
    const pair = plugboard.querySelector(`.mapping-cell[data-pair-key="${pairKey}"]`);
    if (pair) {
      pair.classList.add("component-active");
    }
    return;
  }

  if (step.component === "reflector") {
    const pair = reflectorDisplay.querySelector(`.reflector-pair[data-pair-key="${pairKey}"]`);
    if (pair) {
      pair.classList.add("component-active");
    }
  }
}

async function animateSignalPath(inputLetter, outputLetter, trace) {
  clearComponentHighlights();
  clearKeyHighlights();
  activateKey(inputLetter, "input-active");
  setCurrentTraceValue(inputLetter);
  await sleep(highlightDelayMs);

  for (const step of trace) {
    clearComponentHighlights();
    highlightTraceStep(step);
    setCurrentTraceValue(step.to);
    await sleep(highlightDelayMs);
  }

  activateKey(outputLetter, "output-active");
  setCurrentTraceValue(outputLetter);
  await sleep(highlightDelayMs);
  clearComponentHighlights();
  clearKeyHighlights();
}

async function startSession() {
  const numRotors = Number(numRotorsInput.value || 3);
  const rawSeed = seedInput.value.trim();
  const payload = {
    numRotors,
    seed: rawSeed === "" ? null : Number(rawSeed),
    randomizePositions: randomizePositionsInput.checked,
  };
  const data = await postJson("/api/session", payload);
  sessionId = data.sessionId;
  renderState(data.state);
  setSessionEnabled(true);
  setBusyState(false);
  const startPositions = data.state.rotorPositions.join(", ");
  setTimelineText(`Session ready (${sessionId.slice(0, 8)}...) | Start positions: [${startPositions}]`);
  setCurrentTraceValue("-");
}

async function refreshState() {
  if (!sessionId) {
    return;
  }
  const data = await postJson("/api/state", { sessionId });
  renderState(data.state);
}

async function encryptKey(letter, options = {}) {
  const { appendToBoxes = true } = options;
  if (!sessionId) {
    setTimelineText("Start a session first.");
    return;
  }
  setBusyState(true);
  const data = await postJson("/api/keypress", { sessionId, letter });
  lastInput.textContent = data.input;
  lastOutput.textContent = data.output;
  if (appendToBoxes) {
    appendTypedPair(data.input, data.output);
  }
  if (Array.isArray(data.trace) && data.trace.length > 0) {
    await animateSignalPath(data.input, data.output, data.trace);
  } else {
    await animateKeySequence(data.input, data.output);
  }
  renderState(data.state);
  setTimelineText(
    `Pre: [${data.timeline.prePositions.join(", ")}] | Post: [${data.timeline.postPositions.join(", ")}]`
  );
  setBusyState(false);
}

async function encryptMessage() {
  if (!sessionId) {
    setTimelineText("Start a session first.");
    return;
  }
  cipherOutput.value = "";
  setBusyState(true);
  const message = messageInput.value.toUpperCase();
  const output = [];

  for (const character of message) {
    if (!alphabet.includes(character)) {
      output.push(character);
      cipherOutput.value = output.join("");
      continue;
    }

    const data = await postJson("/api/keypress", { sessionId, letter: character });
    lastInput.textContent = data.input;
    lastOutput.textContent = data.output;
    output.push(data.output);
    if (Array.isArray(data.trace) && data.trace.length > 0) {
      await animateSignalPath(data.input, data.output, data.trace);
    } else {
      await animateKeySequence(data.input, data.output);
    }
    renderState(data.state);
    cipherOutput.value = output.join("");
  }

  setTimelineText("Message encrypted with animated key sequence.");
  setBusyState(false);
}

async function resetRotors() {
  if (!sessionId) {
    setTimelineText("Start a session first.");
    return;
  }
  setBusyState(true);
  let data;
  try {
    data = await postJson("/api/reset", { sessionId });
  } catch (error) {
    const message = String(error.message || "");
    if (!message.includes("404")) {
      setBusyState(false);
      throw error;
    }
    data = await postJson("/api/encrypt", { sessionId, message: "" });
  }
  renderState(data.state);
  setTimelineText(
    `Rotors reset. Pre: [${data.timeline.prePositions.join(", ")}] | Post: [${data.timeline.postPositions.join(", ")}]`
  );
  setBusyState(false);
}

startSessionBtn.addEventListener("click", async () => {
  try {
    setBusyState(true);
    await startSession();
  } catch (error) {
    setBusyState(false);
    setTimelineText(`Error: ${error.message}`);
  }
});

encryptMessageBtn.addEventListener("click", async () => {
  try {
    await encryptMessage();
  } catch (error) {
    setBusyState(false);
    setTimelineText(`Error: ${error.message}`);
  }
});

clearMessageBtn.addEventListener("click", () => {
  if (!sessionId || isBusy) {
    return;
  }
  messageInput.value = "";
  cipherOutput.value = "";
  setCurrentTraceValue("-");
  setTimelineText("Message and cypher cleared.");
});

copyCipherToInputBtn.addEventListener("click", async () => {
  if (!sessionId || isBusy) {
    return;
  }

  const cypherText = cipherOutput.value;
  messageInput.value = cypherText;
  cipherOutput.value = "";

  try {
    await resetRotors();
    setTimelineText("Ready to decrypt: cypher moved to input, cypher cleared, and rotors reset.");
  } catch (error) {
    setBusyState(false);
    setTimelineText(`Error: ${error.message}`);
  }
});

animationDelayInput.addEventListener("input", () => {
  updateAnimationDelay();
});

window.addEventListener("keydown", async (event) => {
  const target = event.target;
  const isTypingField =
    target instanceof HTMLElement &&
    (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable);

  if (isTypingField) {
    return;
  }

  if (event.key === " " && sessionId && !isBusy) {
    event.preventDefault();
    appendTypedPair(" ", " ");
    lastInput.textContent = "␠";
    lastOutput.textContent = "␠";
    setCurrentTraceValue(" ");
    setTimelineText("Space appended.");
    return;
  }

  const letter = event.key.toUpperCase();
  if (!alphabet.includes(letter) || !sessionId || isBusy) {
    return;
  }
  try {
    await encryptKey(letter);
  } catch (error) {
    setBusyState(false);
    setTimelineText(`Error: ${error.message}`);
  }
});

renderKeyboard();
updateAnimationDelay();
setSessionEnabled(false);
refreshState();
