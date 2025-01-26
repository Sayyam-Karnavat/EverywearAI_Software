// Prevent duplicate icon injection
if (!document.getElementById("draggable-chatgpt-icon")) {
    // Create the draggable icon
    const icon = document.createElement("div");
    icon.id = "draggable-chatgpt-icon";
    icon.innerHTML = '<img src="' + chrome.runtime.getURL("icon.png") + '" alt="ChatGPT Icon" />';
  
    // Style the icon
    icon.style.position = "fixed";
    icon.style.top = "20px";
    icon.style.left = "20px";
    icon.style.width = "50px";
    icon.style.height = "50px";
    icon.style.cursor = "grab";
    icon.style.zIndex = "9999";
    icon.style.borderRadius = "50%";
    icon.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
  
    // Append the icon to the document body
    document.body.appendChild(icon);
  
    // Draggable functionality
    let isDragging = false;
    let offsetX = 0;
    let offsetY = 0;
  
    icon.addEventListener("mousedown", (e) => {
      isDragging = true;
      offsetX = e.clientX - icon.getBoundingClientRect().left;
      offsetY = e.clientY - icon.getBoundingClientRect().top;
      icon.style.cursor = "grabbing";
    });
  
    document.addEventListener("mousemove", (e) => {
      if (isDragging) {
        icon.style.left = `${e.clientX - offsetX}px`;
        icon.style.top = `${e.clientY - offsetY}px`;
      }
    });
  
    document.addEventListener("mouseup", () => {
      isDragging = false;
      icon.style.cursor = "grab";
    });
  
    // Open ChatGPT in a popup window when clicked
    icon.addEventListener("click", () => {
      // Create a new popup window
      const popup = window.open("", "ChatGPT", "width=400,height=600,top=100,left=100");
  
      // Create an iframe and set the ChatGPT URL as its source
      const iframe = document.createElement("iframe");
      iframe.src = "https://chat.openai.com";
      iframe.style.width = "100%";
      iframe.style.height = "100%";
      iframe.style.border = "none";
  
      // Append the iframe to the popup window's document
      popup.document.body.appendChild(iframe);
    });
  }
  