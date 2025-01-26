chrome.action.onClicked.addListener((tab) => {
    if (tab.url && tab.url.startsWith("chrome://")) {
      console.log('Cannot inject on chrome:// URLs');
      return;
    }
  
    // Inject content script dynamically
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: injectDraggableIcon
    });
  });
  
  // Function to inject the draggable icon directly
  function injectDraggableIcon() {
    if (!document.getElementById("draggable-chatgpt-icon")) {
      const icon = document.createElement("div");
      icon.id = "draggable-chatgpt-icon";
      icon.innerHTML = '<img src="' + chrome.runtime.getURL("icon.png") + '" alt="ChatGPT Icon" />';
      icon.style.position = "fixed";
      icon.style.top = "20px";
      icon.style.left = "20px";
      icon.style.width = "50px";
      icon.style.height = "50px";
      icon.style.cursor = "grab";
      icon.style.zIndex = "9999";
      icon.style.borderRadius = "50%";
      icon.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
      document.body.appendChild(icon);
  
      // Add draggable functionality
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
  
      icon.addEventListener("click", () => {
        const popup = window.open("", "ChatGPT", "width=400,height=600,top=100,left=100");
        const iframe = document.createElement("iframe");
        iframe.src = "https://chat.openai.com";
        iframe.style.width = "100%";
        iframe.style.height = "100%";
        iframe.style.border = "none";
        popup.document.body.appendChild(iframe);
      });
    }
  }
  