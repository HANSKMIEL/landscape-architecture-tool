#!/usr/bin/env python3
"""
DOM Re-rendering Investigation and Fix for Plants Component Input Fields

This script investigates potential DOM re-rendering issues that could cause
input field focus loss after each keystroke and provides fixes.

Based on the analysis in the comments, the issue is likely related to:
1. DOM re-rendering during state updates
2. Event handling causing component re-creation
3. Modal or form state management issues
"""

import json
import os
from datetime import datetime


def analyze_plants_component():
    """Analyze the Plants component for potential DOM re-rendering issues"""

    component_path = (
        "/home/runner/work/landscape-architecture-tool/landscape-architecture-tool/frontend/src/components/Plants.jsx"
    )

    if not os.path.exists(component_path):
        return {"error": "Plants.jsx component not found"}

    with open(component_path) as f:
        content = f.read()

    analysis = {
        "timestamp": datetime.now().isoformat(),
        "component_analysis": {},
        "potential_issues": [],
        "recommendations": [],
        "fixes_to_implement": [],
    }

    # Check for useCallback usage
    if "useCallback" in content:
        analysis["component_analysis"]["uses_useCallback"] = True
        analysis["component_analysis"]["useCallback_count"] = content.count("useCallback")
    else:
        analysis["potential_issues"].append("Missing useCallback for event handlers")

    # Check for proper form state management
    if "setFormData" in content:
        analysis["component_analysis"]["has_form_state"] = True
        # Check if setFormData is used with functional updates
        if "prevData =>" in content:
            analysis["component_analysis"]["uses_functional_updates"] = True
        else:
            analysis["potential_issues"].append("Form state updates might not be functional")

    # Check for modal re-rendering issues
    if "showAddModal" in content and "showEditModal" in content:
        analysis["component_analysis"]["has_modal_state"] = True

        # Check if form is properly isolated in modal
        if "PlantForm" in content:
            analysis["component_analysis"]["has_isolated_form_component"] = True
        else:
            analysis["potential_issues"].append("Form might not be properly isolated")

    # Check for key prop usage in lists
    if "key={" in content:
        analysis["component_analysis"]["uses_key_props"] = True
    else:
        analysis["potential_issues"].append("Missing key props in list rendering")

    # Check for controlled vs uncontrolled inputs
    if "value={" in content and "onChange={" in content:
        analysis["component_analysis"]["uses_controlled_inputs"] = True
    else:
        analysis["potential_issues"].append("Inputs might not be properly controlled")

    # Analyze specific patterns that could cause re-rendering
    problematic_patterns = [
        ("inline function definitions", "onClick={() =>"),
        ("inline object creation", "style={{"),
        ("inline array creation", "className={["),
        ("direct state mutation", "formData."),
    ]

    for pattern_name, pattern in problematic_patterns:
        if pattern in content:
            analysis["potential_issues"].append(f"Found {pattern_name}: {pattern}")

    # Generate recommendations
    analysis["recommendations"] = [
        "Ensure all event handlers use useCallback with proper dependencies",
        "Use functional state updates for complex state objects",
        "Avoid inline function definitions in JSX",
        "Memoize expensive computations with useMemo",
        "Ensure form components are properly isolated",
        "Use React.memo for heavy child components",
    ]

    return analysis


def create_optimized_input_handler():
    """Create an optimized input handler to prevent focus loss"""

    return """
// Optimized Input Handler Fix for Plants Component
// This fix addresses potential DOM re-rendering issues causing focus loss

import React, { useState, useCallback, useMemo, useRef } from 'react';

// Fixed input handler with proper memoization
const useOptimizedFormHandler = (initialFormData) => {
  const [formData, setFormData] = useState(initialFormData);
  const formRef = useRef(null);
  
  // Memoized input change handler to prevent re-creation
  const handleInputChange = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    
    // Use functional update to prevent stale closures
    setFormData(prevData => ({
      ...prevData,
      [name]: type === 'checkbox' ? checked : value
    }));
  }, []); // Empty dependency array since we use functional updates
  
  // Memoized reset function
  const resetForm = useCallback(() => {
    setFormData(initialFormData);
  }, [initialFormData]);
  
  return {
    formData,
    handleInputChange,
    resetForm,
    formRef
  };
};

// Memoized Input Component to prevent unnecessary re-renders
const MemoizedInput = React.memo(({ 
  name, 
  value, 
  onChange, 
  placeholder, 
  type = "text",
  required = false,
  ...props 
}) => {
  return (
    <input
      name={name}
      value={value || ''}
      onChange={onChange}
      placeholder={placeholder}
      type={type}
      required={required}
      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
      {...props}
    />
  );
});

// Fixed Form Component with proper memoization
const OptimizedPlantForm = React.memo(({ 
  isEdit = false, 
  onSubmit, 
  onCancel, 
  initialData = {} 
}) => {
  const { formData, handleInputChange, resetForm, formRef } = useOptimizedFormHandler(initialData);
  
  // Submit handler with useCallback
  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    onSubmit(formData);
  }, [formData, onSubmit]);
  
  // Cancel handler with useCallback
  const handleCancel = useCallback(() => {
    resetForm();
    onCancel();
  }, [resetForm, onCancel]);
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <form ref={formRef} onSubmit={handleSubmit} className="space-y-6">
          {/* Form fields using MemoizedInput */}
          <MemoizedInput
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            placeholder="Scientific Name"
            required
          />
          
          <MemoizedInput
            name="common_name"
            value={formData.common_name}
            onChange={handleInputChange}
            placeholder="Common Name"
          />
          
          {/* Additional form fields... */}
          
          <div className="flex justify-end space-x-2 pt-4">
            <button 
              type="button" 
              onClick={handleCancel}
              className="px-4 py-2 border border-gray-300 rounded-md"
            >
              Cancel
            </button>
            <button 
              type="submit"
              className="px-4 py-2 bg-green-600 text-white rounded-md"
            >
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  );
});

export { useOptimizedFormHandler, MemoizedInput, OptimizedPlantForm };
"""


def create_focus_debugging_script():
    """Create a script to debug focus issues in real-time"""

    return """
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
"""


def generate_fix_implementation():
    """Generate the actual fix implementation for the Plants component"""

    return {
        "timestamp": datetime.now().isoformat(),
        "analysis_results": analyze_plants_component(),
        "optimized_input_handler": create_optimized_input_handler(),
        "focus_debugging_script": create_focus_debugging_script(),
        "implementation_steps": [
            "1. Replace handleInputChange with useCallback and empty dependencies",
            "2. Ensure all form state updates use functional updates",
            "3. Memoize the PlantForm component with React.memo",
            "4. Create optimized input components with proper memoization",
            "5. Add focus debugging to track re-rendering issues",
            "6. Test input behavior with character-by-character typing",
        ],
        "test_cases": [
            "Type rapidly in scientific name field",
            "Tab between multiple input fields",
            "Use backspace and delete keys",
            "Test with different browsers",
            "Verify focus retention during state updates",
        ],
    }


if __name__ == "__main__":
    print("🔍 Analyzing Plants component for DOM re-rendering issues...")

    # Generate comprehensive analysis and fixes
    analysis_results = generate_fix_implementation()

    # Save results
    with open("dom_re_rendering_analysis.json", "w") as f:
        json.dump(analysis_results, f, indent=2)

    # Create optimized component file
    with open("OptimizedPlantForm.jsx", "w") as f:
        f.write(analysis_results["optimized_input_handler"])

    # Create debugging utilities
    with open("FocusDebugging.jsx", "w") as f:
        f.write(analysis_results["focus_debugging_script"])

    print("✅ Analysis complete!")
    print("\n📊 Analysis Results:")
    print(
        f"- Render count analysis: {len(analysis_results['analysis_results']['potential_issues'])} potential issues found"
    )
    print(f"- Component analysis: {len(analysis_results['analysis_results']['component_analysis'])} patterns analyzed")
    print(f"- Recommendations: {len(analysis_results['analysis_results']['recommendations'])} optimization suggestions")

    print("\n🔧 Generated Files:")
    print("- dom_re_rendering_analysis.json: Complete analysis results")
    print("- OptimizedPlantForm.jsx: Optimized form component with fix")
    print("- FocusDebugging.jsx: Focus debugging utilities")

    print("\n🎯 Key Findings:")
    for issue in analysis_results["analysis_results"]["potential_issues"]:
        print(f"  - {issue}")

    print("\n📋 Next Steps:")
    for _i, step in enumerate(analysis_results["implementation_steps"], 1):
        print(f"  {step}")

    print("\n✨ Root Cause Likely Identified:")
    print("  Input field focus loss is likely caused by DOM re-rendering during state updates.")
    print("  The fix involves proper memoization of input handlers and form components.")
