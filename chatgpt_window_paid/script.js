const draggableIcon = document.getElementById('draggable-icon');
const floatingWindow = document.getElementById('floating-window');
const closeWindowButton = document.getElementById('close-window');
const apiKeyContainer = document.getElementById('api-key-container');
const apiKeyInput = document.getElementById('api-key-input');
const saveApiKeyButton = document.getElementById('save-api-key');
const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const messages = document.getElementById('messages');

let apiKey = ''; // API key stored temporarily in memory

// Draggable Icon Logic
let offsetX, offsetY;
draggableIcon.addEventListener('mousedown', (e) => {
  offsetX = e.clientX - draggableIcon.getBoundingClientRect().left;
  offsetY = e.clientY - draggableIcon.getBoundingClientRect().top;

  function moveAt(event) {
    draggableIcon.style.left = event.clientX - offsetX + 'px';
    draggableIcon.style.top = event.clientY - offsetY + 'px';
  }

  function onMouseMove(event) {
    moveAt(event);
  }

  document.addEventListener('mousemove', onMouseMove);

  draggableIcon.addEventListener('mouseup', () => {
    document.removeEventListener('mousemove', onMouseMove);
  });
});

// Open/Close Chat Window
draggableIcon.addEventListener('click', () => {
  floatingWindow.style.display =
    floatingWindow.style.display === 'block' ? 'none' : 'block';
});

closeWindowButton.addEventListener('click', () => {
  floatingWindow.style.display = 'none';
});

// Save API Key
saveApiKeyButton.addEventListener('click', () => {
  const enteredApiKey = apiKeyInput.value.trim();
  if (!enteredApiKey) {
    apiKeyContainer.classList.add('error');
    return;
  }

  apiKeyContainer.classList.remove('error');
  apiKey = enteredApiKey; // Save the API key in memory
  apiKeyContainer.style.display = 'none'; // Hide API key input
  chatContainer.style.display = 'flex'; // Show the chat container
});

// Chat Functionality
chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  const userMessage = userInput.value.trim();
  if (!userMessage) return;

  addMessage(userMessage, 'user-message');
  userInput.value = '';
  messages.scrollTop = messages.scrollHeight;

  // Show a "typing" message
  const botTypingMessage = addMessage('ChatGPT is typing...', 'bot-message');

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`, // Use the saved API key
      },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages: [{ role: 'user', content: userMessage }],
      }),
    });

    const data = await response.json();
    const botReply = data.choices[0].message.content;

    // Update bot message with the actual reply
    botTypingMessage.textContent = botReply;
  } catch (error) {
    botTypingMessage.textContent = 'Error: Unable to fetch response.';
  }

  messages.scrollTop = messages.scrollHeight;
});

// Helper Function to Add Messages
function addMessage(content, className) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${className}`;
  messageDiv.textContent = content;
  messages.appendChild(messageDiv);
  return messageDiv;
}
