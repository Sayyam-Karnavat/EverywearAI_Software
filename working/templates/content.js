console.log("content.js loaded");

document.addEventListener("DOMContentLoaded", () => {
  // Create the draggable circular icon
  const circularIcon = document.createElement("div");
  circularIcon.id = "circular-icon";
  circularIcon.innerText = "💬";
  document.body.appendChild(circularIcon);

  // Create a container for tick and cross buttons
  const actionButtons = document.createElement("div");
  actionButtons.id = "action-buttons";
  actionButtons.style.display = "none"; // Hidden by default
  actionButtons.innerHTML = `
    <button id="tick-btn">✔️</button>
    <button id="cross-btn">❌</button>
  `;
  document.body.appendChild(actionButtons);

  // Fetch and create the overlay container but keep it hidden initially
  fetch("overlay.html")
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to load overlay.html");
      }
      return response.text();
    })
    .then((html) => {
      const overlayContainer = document.createElement("div");
      overlayContainer.innerHTML = html;
      overlayContainer.id = "llm-overlay";
      overlayContainer.style.display = "none"; // Initially hidden
      document.body.appendChild(overlayContainer);

      // Add drag functionality for the circular icon
      let isDragging = false;
      circularIcon.onmousedown = function (e) {
        let offsetX = e.clientX - circularIcon.offsetLeft;
        let offsetY = e.clientY - circularIcon.offsetTop;

        function mouseMoveHandler(event) {
          isDragging = true;
          circularIcon.style.left = `${event.clientX - offsetX}px`;
          circularIcon.style.top = `${event.clientY - offsetY}px`;
          circularIcon.style.position = "fixed";

          // Move action buttons along with the icon
          actionButtons.style.left = `${event.clientX - offsetX + 60}px`;
          actionButtons.style.top = `${event.clientY - offsetY}px`;
        }

        function mouseUpHandler() {
          document.removeEventListener("mousemove", mouseMoveHandler);
          document.removeEventListener("mouseup", mouseUpHandler);
          if (isDragging) {
            actionButtons.style.display = "block"; // Show tick and cross buttons
          }
        }

        document.addEventListener("mousemove", mouseMoveHandler);
        document.addEventListener("mouseup", mouseUpHandler);
      };

      // Handle tick button click
      actionButtons.querySelector("#tick-btn").addEventListener("click", () => {
        // Set the Chat UI to the icon's current position
        overlayContainer.style.left = circularIcon.style.left;
        overlayContainer.style.top = circularIcon.style.top;
        overlayContainer.style.position = "fixed";
        overlayContainer.style.display = "flex"; // Show chat overlay

        circularIcon.style.display = "none"; // Hide the icon
        actionButtons.style.display = "none"; // Hide the buttons
      });

      // Handle cross button click
      actionButtons.querySelector("#cross-btn").addEventListener("click", () => {
        if (overlayContainer.style.display === "flex") {
          overlayContainer.style.display = "none";
          circularIcon.style.display = "block";
          actionButtons.style.display = "none";
        } else {
          circularIcon.remove();
          actionButtons.remove();
        }
      });

      // Add drag functionality to the Chat UI
      overlayContainer.querySelector("#draggable-header").onmousedown = function (e) {
        let offsetX = e.clientX - overlayContainer.offsetLeft;
        let offsetY = e.clientY - overlayContainer.offsetTop;

        function mouseMoveHandler(event) {
          overlayContainer.style.left = `${event.clientX - offsetX}px`;
          overlayContainer.style.top = `${event.clientY - offsetY}px`;
          overlayContainer.style.position = "fixed";
        }

        function mouseUpHandler() {
          document.removeEventListener("mousemove", mouseMoveHandler);
          document.removeEventListener("mouseup", mouseUpHandler);
        }

        document.addEventListener("mousemove", mouseMoveHandler);
        document.addEventListener("mouseup", mouseUpHandler);
      };

      // Close the chat UI and revert to the icon
      overlayContainer.querySelector("#close-btn").addEventListener("click", () => {
        circularIcon.style.left = overlayContainer.style.left;
        circularIcon.style.top = overlayContainer.style.top;
        overlayContainer.style.display = "none";
        circularIcon.style.display = "block";
      });

      // Handle chat functionality
      const sendBtn = overlayContainer.querySelector("#send-btn");
      const queryInput = overlayContainer.querySelector("#query-input");
      const messages = overlayContainer.querySelector("#messages");

      sendBtn.addEventListener("click", () => {
        const userMessage = queryInput.value.trim();
        if (userMessage) {
          const userMessageElement = document.createElement("div");
          userMessageElement.textContent = `User: ${userMessage}`;
          messages.appendChild(userMessageElement);

          // Make API call to Flask backend
          fetch(window.backendURL, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ query: userMessage }),
          })
            .then((response) => response.json())
            .then((data) => {
              const botMessageElement = document.createElement("div");
              botMessageElement.textContent = `LLM: ${data.response}`;
              messages.appendChild(botMessageElement);
            })
            .catch((error) => {
              const errorMessageElement = document.createElement("div");
              errorMessageElement.textContent = "Error: Unable to fetch response.";
              messages.appendChild(errorMessageElement);
              console.error("API call error:", error);
            });

          queryInput.value = ""; // Clear the input box after sending
        }
      });
    })
    .catch((error) => console.error("Error loading overlay:", error));
});
