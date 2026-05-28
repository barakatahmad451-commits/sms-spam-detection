const smsInput = document.getElementById('sms-input');
const classifyBtn = document.getElementById('classify-btn');
const resultBadge = document.getElementById('result-badge');
const resultText = document.getElementById('result-text');
const spamScore = document.getElementById('spam-score');
const hamScore = document.getElementById('ham-score');
const resultExplanation = document.getElementById('result-explanation');
const vocabSize = document.getElementById('vocab-size');

const updateStatus = ({ prediction, spamProbability, hamProbability, explanation, matchedTokens, vocabularySize }) => {
  resultBadge.textContent = prediction === 'Spam' ? 'Spam detected' : 'Looks safe';
  resultBadge.style.background = prediction === 'Spam' ? 'rgba(248, 113, 113, 0.16)' : 'rgba(34, 211, 238, 0.16)';
  resultBadge.style.color = prediction === 'Spam' ? '#fecaca' : '#a5f3fc';
  resultText.innerHTML = `Prediction: <strong>${prediction}</strong>`;
  spamScore.textContent = `${spamProbability}%`;
  hamScore.textContent = `${hamProbability}%`;
  resultExplanation.innerHTML = `<strong>Why this result?</strong> ${explanation} <br><br><strong>Matched tokens:</strong> ${matchedTokens.join(', ')}`;
  vocabSize.textContent = vocabularySize.toLocaleString();
};

const sendMessage = async () => {
  const message = smsInput.value.trim();
  if (!message) {
    alert('Please paste an SMS message to classify.');
    smsInput.focus();
    return;
  }

  classifyBtn.disabled = true;
  classifyBtn.textContent = 'Scanning...';

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Unable to classify message.');
    }

    updateStatus(data);
  } catch (error) {
    resultBadge.textContent = 'Error';
    resultText.textContent = error.message;
    resultExplanation.textContent = 'Try again with a different message or refresh the page.';
  } finally {
    classifyBtn.disabled = false;
    classifyBtn.textContent = 'Scan for Spam';
  }
};

classifyBtn.addEventListener('click', sendMessage);

smsInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && event.ctrlKey) {
    sendMessage();
  }
});
