const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();

// Proxy configuration
app.use(
  '/chatgpt',
  createProxyMiddleware({
    target: 'https://chat.openai.com',
    changeOrigin: true,
    pathRewrite: {
      '^/chatgpt': '', // Remove "/chatgpt" from the URL
    },
  })
);

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Proxy server running on http://localhost:${PORT}`);
});
