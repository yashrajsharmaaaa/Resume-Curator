/**
 * useFormValidation Hook for Resume Curator
 * 
 * Provides comprehensive form validation with real-time validation,
 * error handling, and form submission prevention for invalid inputs.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { 
  validateForm, 
  ValidationSchemas, 
  createDebouncedValidator,
  sanitizeText 
} from '../utils/validation';

/**
 * Form validation hook with real-time validation and error handling
 */
export function useFormValidation(initialValues = {}, validationSchema = {}, options = {}) {
  const {
    validateOnChange = true,
    validateOnBlur = true,
    sanitizeInputs = true,
    debounceDelay = 300,
    onValidationChange = null
  } = options;

  // Form state
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [warnings, setWarnings] = useState({});
  const [touched, setTouched] = useState({});
  const [isValidating, setIsValidating] = useState(false);
  const [isValid, setIsValid] = useState(false);
  const [hasBeenSubmitted, setHasBeenSubmitted] = useState(false);

  // Refs for debounced validation
  const validationTimeouts = useRef({});
  const debouncedValidator = useRef(
    createDebouncedValidator((formData, schema) => {
      return validateForm(formData, schema);
    }, debounceDelay)
  );

  // Validate entire form
  const validateFormData = useCallback(async (formData = values, schema = validationSchema) => {
    setIsValidating(true);
    
    try {
      const result = await debouncedValidator.current(formData, schema);
      
      // Extract field-specific errors and warnings
      const fieldErrors = {};
      const fieldWarnings = {};
      
      result.errors.forEach(error => {
        if (error.field) {
          if (!fieldErrors[error.field]) {
            fieldErrors[error.field] = [];
          }
          fieldErrors[error.field].push(error.message);
        }
      });
      
      result.warnings.forEach(warning => {
        if (warning.field) {
          if (!fieldWarnings[warning.field]) {
            fieldWarnings[warning.field] = [];
          }
          fieldWarnings[warning.field].push(warning.message);
        }
      });
      
      setErrors(fieldErrors);
      setWarnings(fieldWarnings);
      setIsValid(result.isValid);
      
      // Call external validation change handler
      if (onValidationChange) {
        onValidationChange({
          isValid: result.isValid,
          errors: fieldErrors,
          warnings: fieldWarnings,
          values: formData
        });
      }
      
      return result;
    } catch (error) {
      console.error('Form validation error:', error);
      setIsValid(false);
      return { isValid: false, errors: [{ message: 'Validation failed' }], warnings: [] };
    } finally {
      setIsValidating(false);
    }
  }, [values, validationSchema, onValidationChange]);

  // Validate single field
  const validateField = useCallback(async (fieldName, fieldValue, immediate = false) => {
    // Clear existing timeout for this field
    if (validationTimeouts.current[fieldName]) {
      clearTimeout(validationTimeouts.current[fieldName]);
    }

    const performValidation = async () => {
      if (!validationSchema[fieldName]) return;

      setIsValidating(true);
      
      try {
        const fieldSchema = { [fieldName]: validationSchema[fieldName] };
        const fieldData = { [fieldName]: fieldValue };
        const result = await validateForm(fieldData, fieldSchema);
        
        // Update errors and warnings for this field
        setErrors(prev => ({
          ...prev,
          [fieldName]: result.errors
            .filter(error => error.field === fieldName)
            .map(error => error.message)
        }));
        
        setWarnings(prev => ({
          ...prev,
          [fieldName]: result.warnings
            .filter(warning => warning.field === fieldName)
            .map(warning => warning.message)
        }));
        
        return result;
      } catch (error) {
        console.error(`Field validation error for ${fieldName}:`, error);
        setErrors(prev => ({
          ...prev,
          [fieldName]: ['Validation failed']
        }));
      } finally {
        setIsValidating(false);
      }
    };

    if (immediate) {
      return await performValidation();
    } else {
      // Debounced validation
      validationTimeouts.current[fieldName] = setTimeout(performValidation, debounceDelay);
    }
  }, [validationSchema, debounceDelay]);

  // Handle field value change
  const handleChange = useCallback((fieldName, value) => {
    // Sanitize input if enabled
    const sanitizedValue = sanitizeInputs && typeof value === 'string' 
      ? sanitizeText(value) 
      : value;

    // Update value
    setValues(prev => ({
      ...prev,
      [fieldName]: sanitizedValue
    }));

    // Clear errors for this field immediately
    setErrors(prev => ({
      ...prev,
      [fieldName]: []
    }));

    // Validate on change if enabled
    if (validateOnChange && (touched[fieldName] || hasBeenSubmitted)) {
      validateField(fieldName, sanitizedValue);
    }
  }, [validateOnChange, touched, hasBeenSubmitted, sanitizeInputs, validateField]);

  // Handle field blur
  const handleBlur = useCallback((fieldName) => {
    // Mark field as touched
    setTouched(prev => ({
      ...prev,
      [fieldName]: true
    }));

    // Validate on blur if enabled
    if (validateOnBlur) {
      validateField(fieldName, values[fieldName], true); // Immediate validation on blur
    }
  }, [validateOnBlur, values, validateField]);

  // Handle field focus
  const handleFocus = useCallback((fieldName) => {
    // Clear errors when user focuses on field (optional UX improvement)
    if (!hasBeenSubmitted) {
      setErrors(prev => ({
        ...prev,
        [fieldName]: []
      }));
    }
  }, [hasBeenSubmitted]);

  // Handle form submission
  const handleSubmit = useCallback(async (onSubmit) => {
    setHasBeenSubmitted(true);
    
    // Mark all fields as touched
    const allFieldsTouched = Object.keys(validationSchema).reduce((acc, field) => {
      acc[field] = true;
      return acc;
    }, {});
    setTouched(allFieldsTouched);

    // Validate entire form
    const validationResult = await validateFormData();
    
    if (validationResult.isValid && onSubmit) {
      try {
        await onSubmit(values, validationResult);
      } catch (error) {
        console.error('Form submission error:', error);
        // Handle submission error
        setErrors(prev => ({
          ...prev,
          _form: ['Submission failed. Please try again.']
        }));
      }
    }

    return validationResult;
  }, [validationSchema, validateFormData, values]);

  // Reset form
  const reset = useCallback((newValues = initialValues) => {
    setValues(newValues);
    setErrors({});
    setWarnings({});
    setTouched({});
    setIsValid(false);
    setHasBeenSubmitted(false);
    setIsValidating(false);
    
    // Clear all validation timeouts
    Object.values(validationTimeouts.current).forEach(clearTimeout);
    validationTimeouts.current = {};
  }, [initialValues]);

  // Set field value programmatically
  const setFieldValue = useCallback((fieldName, value, shouldValidate = true) => {
    const sanitizedValue = sanitizeInputs && typeof value === 'string' 
      ? sanitizeText(value) 
      : value;

    setValues(prev => ({
      ...prev,
      [fieldName]: sanitizedValue
    }));

    if (shouldValidate && (touched[fieldName] || hasBeenSubmitted)) {
      validateField(fieldName, sanitizedValue);
    }
  }, [sanitizeInputs, touched, hasBeenSubmitted, validateField]);

  // Set field error programmatically
  const setFieldError = useCallback((fieldName, error) => {
    setErrors(prev => ({
      ...prev,
      [fieldName]: Array.isArray(error) ? error : [error]
    }));
    setIsValid(false);
  }, []);

  // Clear field error
  const clearFieldError = useCallback((fieldName) => {
    setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[fieldName];
      return newErrors;
    });
  }, []);

  // Get field props for easy integration with form components
  const getFieldProps = useCallback((fieldName) => ({
    name: fieldName,
    value: values[fieldName] || '',
    onChange: (value) => handleChange(fieldName, value),
    onBlur: () => handleBlur(fieldName),
    onFocus: () => handleFocus(fieldName),
    error: errors[fieldName]?.[0] || null,
    errors: errors[fieldName] || [],
    warnings: warnings[fieldName] || [],
    touched: touched[fieldName] || false,
    hasError: Boolean(errors[fieldName]?.length),
    hasWarning: Boolean(warnings[fieldName]?.length)
  }), [values, errors, warnings, touched, handleChange, handleBlur, handleFocus]);

  // Get form props
  const getFormProps = useCallback(() => ({
    onSubmit: (e) => {
      e.preventDefault();
      return handleSubmit();
    },
    noValidate: true // Disable browser validation
  }), [handleSubmit]);

  // Effect to validate form when values change (for cross-field validation)
  useEffect(() => {
    if (hasBeenSubmitted || Object.keys(touched).length > 0) {
      validateFormData();
    }
  }, [values, hasBeenSubmitted, touched, validateFormData]);

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      Object.values(validationTimeouts.current).forEach(clearTimeout);
    };
  }, []);

  return {
    // Form state
    values,
    errors,
    warnings,
    touched,
    isValid,
    isValidating,
    hasBeenSubmitted,
    
    // Form actions
    handleChange,
    handleBlur,
    handleFocus,
    handleSubmit,
    reset,
    setFieldValue,
    setFieldError,
    clearFieldError,
    validateField,
    validateFormData,
    
    // Helper functions
    getFieldProps,
    getFormProps,
    
    // Utility functions
    hasErrors: Object.keys(errors).some(key => errors[key]?.length > 0),
    hasWarnings: Object.keys(warnings).some(key => warnings[key]?.length > 0),
    getFieldError: (fieldName) => errors[fieldName]?.[0] || null,
    getFieldWarning: (fieldName) => warnings[fieldName]?.[0] || null,
    isFieldTouched: (fieldName) => touched[fieldName] || false,
    isFieldValid: (fieldName) => !errors[fieldName]?.length
  };
}

/**
 * Predefined validation hooks for common forms
 */
export function useResumeUploadValidation(initialValues = {}, options = {}) {
  return useFormValidation(
    initialValues,
    ValidationSchemas.resumeUpload,
    options
  );
}

export function useJobDescriptionValidation(initialValues = {}, options = {}) {
  return useFormValidation(
    initialValues,
    ValidationSchemas.jobDescriptionForm,
    options
  );
}

export function useAnalysisFormValidation(initialValues = {}, options = {}) {
  return useFormValidation(
    initialValues,
    ValidationSchemas.analysisForm,
    options
  );
}

export function useContactFormValidation(initialValues = {}, options = {}) {
  return useFormValidation(
    initialValues,
    ValidationSchemas.contactForm,
    options
  );
}

export default useFormValidation;