// Check if SpeechRecognition and SpeechSynthesisUtterance are available
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const SpeechSynthesisUtterance = window.SpeechSynthesisUtterance;

if (!SpeechRecognition || !SpeechSynthesisUtterance) {
  alert("Your browser does not support speech recognition or speech synthesis.");
}

// Start listening for speech input
function startListening() {
  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false; // We don't need interim results
  recognition.maxAlternatives = 1;

  recognition.start();

  recognition.onresult = function (event) {
    const transcript = event.results[0][0].transcript;
    addToConversation("🧑‍💬 You: " + transcript, "user-message");
    fetchAIResponse(transcript);
  };

  recognition.onerror = function (event) {
    addToConversation("❌ Error: " + event.error, "error-message");
  };

  recognition.onstart = function () {
    addToConversation("🔴 Listening...", "user-message");
  };

  recognition.onend = function () {
    addToConversation("🟢 Listening stopped.", "assistant-message");
  };
}

// Fetch AI response from Gemini API
function fetchAIResponse(message) {
  fetch("/get-response", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  })
    .then(res => res.json())
    .then(data => {
      addToConversation("🤖 Assistant: " + data.reply, "assistant-message");
      speakText(data.reply);
    })
    .catch(err => {
      addToConversation("⚠️ Failed to get response.", "error-message");
      console.error(err);
    });
}

// Add message to the conversation UI
function addToConversation(text, className = "") {
  const div = document.getElementById("conversation");
  const p = document.createElement("p");
  p.textContent = text;
  if (className) {
    p.classList.add(className);
  }
  div.appendChild(p);
  div.scrollTop = div.scrollHeight; // Scroll to the latest message
}

// Speak out the AI response using speech synthesis
function speakText(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'en-US';
  utterance.onerror = function (e) {
    console.error("Speech synthesis error: " + e.error);
  };
  window.speechSynthesis.speak(utterance);
}
