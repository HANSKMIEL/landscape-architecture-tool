
// Focus Debugging Script for Input Field Investigation
// Add this to the Plants component to debug focus loss issues

import { useEffect, useRef } from 'react';

const useFocusDebugger = (formData, componentName = 'PlantForm') => {
  const focusDebugRef = useRef({
    lastFocusedElement: null,
    focusHistory: [],
    renderCount: 0
  });
  
  // Track renders
  focusDebugRef.current.renderCount++;
  
  useEffect(() => {
    const debug = focusDebugRef.current;
    
    // Log render information
    console.log(`[${componentName}] Render #${debug.renderCount}`, {
      formData,
      timestamp: new Date().toISOString()
    });
    
    // Track focus changes
    const handleFocusIn = (e) => {
      debug.lastFocusedElement = e.target;
      debug.focusHistory.push({
        element: e.target.name || e.target.id || e.target.className,
        timestamp: Date.now(),
        type: 'focus'
      });
      
      console.log(`[${componentName}] Focus gained:`, e.target.name || e.target.className);
    };
    
    const handleFocusOut = (e) => {
      debug.focusHistory.push({
        element: e.target.name || e.target.id || e.target.className,
        timestamp: Date.now(),
        type: 'blur'
      });
      
      console.log(`[${componentName}] Focus lost:`, e.target.name || e.target.className);
    };
    
    // Add event listeners
    document.addEventListener('focusin', handleFocusIn);
    document.addEventListener('focusout', handleFocusOut);
    
    return () => {
      document.removeEventListener('focusin', handleFocusIn);
      document.removeEventListener('focusout', handleFocusOut);
    };
  }, [formData, componentName]);
  
  // Return debug information
  return {
    renderCount: focusDebugRef.current.renderCount,
    focusHistory: focusDebugRef.current.focusHistory,
    lastFocusedElement: focusDebugRef.current.lastFocusedElement
  };
};

// Usage in Plants component:
// const debugInfo = useFocusDebugger(formData, 'PlantForm');

export { useFocusDebugger };
