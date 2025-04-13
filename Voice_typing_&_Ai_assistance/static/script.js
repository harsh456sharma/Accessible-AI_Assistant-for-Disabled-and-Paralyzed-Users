let recognition;
let isListening = false;

function toggleSpeech() {
  if (!('webkitSpeechRecognition' in window)) {
    alert("Speech Recognition not supported");
    return;
  }

  if (!recognition) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function(event) {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        finalTranscript += event.results[i][0].transcript;
      }
      document.getElementById('textOutput').value = finalTranscript;
    };

    recognition.onerror = function(event) {
      console.error("Speech recognition error", event.error);
    };
  }

  if (isListening) {
    recognition.stop();
    document.getElementById('status').textContent = "Stopped listening.";
  } else {
    recognition.start();
    document.getElementById('status').textContent = "Listening...";
  }

  isListening = !isListening;
}

function copyText() {
  const text = document.getElementById("textOutput").value;
  navigator.clipboard.writeText(text);
  alert("Copied!");
}

function clearText() {
  document.getElementById("textOutput").value = "";
}
