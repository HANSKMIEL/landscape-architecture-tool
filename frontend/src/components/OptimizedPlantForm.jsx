
// Optimized Input Handler Fix for Plants Component
// This fix addresses potential DOM re-rendering issues causing focus loss

import React, { useState, useCallback, useMemo, useRef } from 'react';

// Fixed input handler with proper memoization
const useOptimizedFormHandler = (initialFormData) => {
  const [__formData, set_formData] = useState(initialFormData);
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
