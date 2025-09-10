import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

console.log('🚀 MAIN.JSX: Starting React application initialization');

// Global error handlers
window.addEventListener('error', (e) => {
  console.error('🔥 GLOBAL ERROR:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
  console.error('🔥 UNHANDLED PROMISE REJECTION:', e.reason);
});

try {
  console.log('🔍 MAIN.JSX: Getting root element');
  const rootElement = document.getElementById('root');
  
  if (rootElement) {
    console.log('✅ MAIN.JSX: Root element found');
    console.log('🔍 MAIN.JSX: Creating React root');
    
    const root = createRoot(rootElement);
    console.log('✅ MAIN.JSX: React root created successfully');
    
    console.log('🔍 MAIN.JSX: Rendering App component');
    
    root.render(
      <StrictMode>
        <App />
      </StrictMode>
    );
    
    console.log('✅ MAIN.JSX: App render call completed');
    
    // Check rendering success
    setTimeout(() => {
      const rootContent = document.getElementById('root').innerHTML;
      if (rootContent.length > 0) {
        console.log('✅ MAIN.JSX: React app rendered successfully');
      } else {
        console.error('🔥 MAIN.JSX: React app failed to render');
      }
    }, 1000);
    
  } else {
    throw new Error('Root element not found in DOM');
  }
  
} catch (error) {
  console.error('🔥 MAIN.JSX: Critical error:', error);
  
  const rootElement = document.getElementById('root');
  if (rootElement) {
    rootElement.innerHTML = `
      <div style="padding: 40px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 8px; margin: 20px;">
        <h1>🔥 React Initialization Error</h1>
        <p>Error: ${error.message}</p>
      </div>
    `;
  }
}
