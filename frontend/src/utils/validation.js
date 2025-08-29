/**
 * Comprehensive validation utilities for Resume Curator
 * 
 * Provides centralized validation logic for forms, files, and user inputs
 * with detailed error messages and real-time validation support.
 */

// Validation error types
export const ValidationErrorTypes = {
  REQUIRED: 'REQUIRED',
  MIN_LENGTH: 'MIN_LENGTH',
  MAX_LENGTH: 'MAX_LENGTH',
  INVALID_FORMAT: 'INVALID_FORMAT',
  INVALID_FILE_TYPE: 'INVALID_FILE_TYPE',
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  FILE_EMPTY: 'FILE_EMPTY',
  WHITESPACE_ONLY: 'WHITESPACE_ONLY',
  INVALID_EMAIL: 'INVALID_EMAIL',
  INVALID_URL: 'INVALID_URL',
  SECURITY_VIOLATION: 'SECURITY_VIOLATION'
};

// File validation constants
export const FileValidation = {
  RESUME_MAX_SIZE: 10 * 1024 * 1024, // 10MB
  RESUME_ACCEPTED_TYPES: ['.pdf', '.doc', '.docx'],
  RESUME_MIME_TYPES: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ]
};

// Text validation constants
export const TextValidation = {
  JOB_DESCRIPTION_MIN_LENGTH: 50,
  JOB_DESCRIPTION_MAX_LENGTH: 10000,
  JOB_DESCRIPTION_WARNING_THRESHOLD: 9000, // 90% of max
  NAME_MAX_LENGTH: 100,
  EMAIL_MAX_LENGTH: 254
};

/**
 * Base validation result structure
 */
export class ValidationResult {
  constructor(isValid = false, errors = [], warnings = [], metadata = {}) {
    this.isValid = isValid;
    this.errors = Array.isArray(errors) ? errors : [errors].filter(Boolean);
    this.warnings = Array.isArray(warnings) ? warnings : [warnings].filter(Boolean);
    this.metadata = metadata;
  }

  // Add error
  addError(type, message, field = null) {
    this.errors.push({ type, message, field });
    this.isValid = false;
    return this;
  }

  // Add warning
  addWarning(type, message, field = null) {
    this.warnings.push({ type, message, field });
    return this;
  }

  // Get first error message
  getFirstError() {
    return this.errors.length > 0 ? this.errors[0].message : null;
  }

  // Get first warning message
  getFirstWarning() {
    return this.warnings.length > 0 ? this.warnings[0].message : null;
  }

  // Check if has errors for specific field
  hasErrorsForField(field) {
    return this.errors.some(error => error.field === field);
  }

  // Get errors for specific field
  getErrorsForField(field) {
    return this.errors.filter(error => error.field === field);
  }
}

/**
 * Validate required field
 */
export function validateRequired(value, fieldName = 'Field') {
  const result = new ValidationResult();
  
  if (value === null || value === undefined || value === '') {
    result.addError(
      ValidationErrorTypes.REQUIRED,
      `${fieldName} is required`,
      fieldName.toLowerCase()
    );
  } else {
    result.isValid = true;
  }
  
  return result;
}

/**
 * Validate text length
 */
export function validateTextLength(text, minLength = 0, maxLength = Infinity, fieldName = 'Text') {
  const result = new ValidationResult();
  const length = text ? text.length : 0;
  
  if (minLength > 0 && length < minLength) {
    result.addError(
      ValidationErrorTypes.MIN_LENGTH,
      `${fieldName} must be at least ${minLength} characters long`,
      fieldName.toLowerCase()
    );
  } else if (length > maxLength) {
    result.addError(
      ValidationErrorTypes.MAX_LENGTH,
      `${fieldName} cannot exceed ${maxLength} characters`,
      fieldName.toLowerCase()
    );
  } else {
    result.isValid = true;
  }
  
  // Add warning if approaching limit
  if (maxLength !== Infinity && length > maxLength * 0.9) {
    const remaining = maxLength - length;
    result.addWarning(
      'APPROACHING_LIMIT',
      `${remaining} characters remaining`,
      fieldName.toLowerCase()
    );
  }
  
  return result;
}

/**
 * Validate whitespace-only content
 */
export function validateNotWhitespaceOnly(text, fieldName = 'Field') {
  const result = new ValidationResult();
  
  if (text && text.trim().length === 0) {
    result.addError(
      ValidationErrorTypes.WHITESPACE_ONLY,
      `${fieldName} cannot contain only whitespace`,
      fieldName.toLowerCase()
    );
  } else {
    result.isValid = true;
  }
  
  return result;
}

/**
 * Validate email format
 */
export function validateEmail(email) {
  const result = new ValidationResult();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (email && !emailRegex.test(email)) {
    result.addError(
      ValidationErrorTypes.INVALID_EMAIL,
      'Please enter a valid email address',
      'email'
    );
  } else {
    result.isValid = true;
  }
  
  return result;
}

/**
 * Validate URL format
 */
export function validateURL(url) {
  const result = new ValidationResult();
  
  try {
    new URL(url);
    result.isValid = true;
  } catch {
    result.addError(
      ValidationErrorTypes.INVALID_URL,
      'Please enter a valid URL',
      'url'
    );
  }
  
  return result;
}

/**
 * Validate file upload
 */
export function validateFile(file, options = {}) {
  const result = new ValidationResult();
  
  const {
    maxSize = FileValidation.RESUME_MAX_SIZE,
    acceptedTypes = FileValidation.RESUME_ACCEPTED_TYPES,
    acceptedMimeTypes = FileValidation.RESUME_MIME_TYPES,
    fieldName = 'File'
  } = options;
  
  // Check if file exists
  if (!file) {
    result.addError(
      ValidationErrorTypes.REQUIRED,
      `${fieldName} is required`,
      fieldName.toLowerCase()
    );
    return result;
  }
  
  // Check file size
  if (file.size === 0) {
    result.addError(
      ValidationErrorTypes.FILE_EMPTY,
      'The selected file is empty. Please choose a valid file.',
      fieldName.toLowerCase()
    );
  } else if (file.size > maxSize) {
    const maxSizeMB = Math.round(maxSize / (1024 * 1024));
    const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
    result.addError(
      ValidationErrorTypes.FILE_TOO_LARGE,
      `File size (${fileSizeMB}MB) exceeds the ${maxSizeMB}MB limit. Please choose a smaller file.`,
      fieldName.toLowerCase()
    );
  }
  
  // Check file type by extension
  const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
  if (!acceptedTypes.includes(fileExtension)) {
    result.addError(
      ValidationErrorTypes.INVALID_FILE_TYPE,
      `File type "${fileExtension}" is not supported. Please upload a file in one of these formats: ${acceptedTypes.join(', ')}`,
      fieldName.toLowerCase()
    );
  }
  
  // Check MIME type if available
  if (file.type && acceptedMimeTypes.length > 0) {
    const isValidMimeType = acceptedMimeTypes.some(mimeType => 
      file.type === mimeType || file.type.startsWith(mimeType.split('/')[0] + '/')
    );
    
    if (!isValidMimeType) {
      result.addError(
        ValidationErrorTypes.INVALID_FILE_TYPE,
        `File type is not supported. Please upload a valid document file.`,
        fieldName.toLowerCase()
      );
    }
  }
  
  // Check file name length
  if (file.name.length > 255) {
    result.addError(
      ValidationErrorTypes.MAX_LENGTH,
      'File name is too long. Please rename your file to be shorter than 255 characters.',
      fieldName.toLowerCase()
    );
  }
  
  // Security checks
  const suspiciousPatterns = [
    /^\./, // Hidden files
    /\.(exe|bat|cmd|scr|vbs|js|jar|com|pif|application)$/i, // Executable files
    /[<>:"|?*]/, // Invalid filename characters
  ];
  
  if (suspiciousPatterns.some(pattern => pattern.test(file.name))) {
    result.addError(
      ValidationErrorTypes.SECURITY_VIOLATION,
      'This file type is not allowed for security reasons. Please upload a document file.',
      fieldName.toLowerCase()
    );
  }
  
  // If no errors, mark as valid
  if (result.errors.length === 0) {
    result.isValid = true;
    
    // Add metadata
    result.metadata = {
      fileName: file.name,
      fileSize: file.size,
      fileType: file.type,
      fileExtension: fileExtension,
      lastModified: new Date(file.lastModified)
    };
  }
  
  return result;
}

/**
 * Validate job description
 */
export function validateJobDescription(text) {
  const result = new ValidationResult();
  
  // Combine multiple validations
  const requiredResult = validateRequired(text, 'Job description');
  const whitespaceResult = validateNotWhitespaceOnly(text, 'Job description');
  const lengthResult = validateTextLength(
    text,
    TextValidation.JOB_DESCRIPTION_MIN_LENGTH,
    TextValidation.JOB_DESCRIPTION_MAX_LENGTH,
    'Job description'
  );
  
  // Merge results
  result.errors = [...requiredResult.errors, ...whitespaceResult.errors, ...lengthResult.errors];
  result.warnings = [...lengthResult.warnings];
  
  // Additional job description specific validations
  if (text && text.trim()) {
    const trimmedText = text.trim();
    
    // Check for very short descriptions
    if (trimmedText.length < 100) {
      result.addWarning(
        'SHORT_CONTENT',
        'Job description is quite short - consider adding more details for better analysis',
        'job_description'
      );
    }
    
    // Check for common keywords that indicate a good job description
    const importantKeywords = [
      'responsibilities', 'requirements', 'qualifications', 'experience',
      'skills', 'education', 'duties', 'role', 'position'
    ];
    
    const foundKeywords = importantKeywords.filter(keyword => 
      trimmedText.toLowerCase().includes(keyword)
    );
    
    if (foundKeywords.length < 3) {
      result.addWarning(
        'INCOMPLETE_CONTENT',
        'Consider including more details about responsibilities, requirements, and qualifications',
        'job_description'
      );
    }
    
    // Check for excessive repetition
    const words = trimmedText.toLowerCase().split(/\s+/);
    const wordCount = {};
    words.forEach(word => {
      if (word.length > 3) { // Only check words longer than 3 characters
        wordCount[word] = (wordCount[word] || 0) + 1;
      }
    });
    
    const repeatedWords = Object.entries(wordCount)
      .filter(([, count]) => count > words.length * 0.05) // More than 5% of total words
      .map(([word]) => word);
    
    if (repeatedWords.length > 0) {
      result.addWarning(
        'REPETITIVE_CONTENT',
        `Some words appear frequently: ${repeatedWords.slice(0, 3).join(', ')}. Consider varying your language.`,
        'job_description'
      );
    }
  }
  
  result.isValid = result.errors.length === 0;
  return result;
}

/**
 * Validate form data
 */
export function validateForm(formData, validationRules) {
  const result = new ValidationResult();
  const fieldResults = {};
  
  for (const [fieldName, rules] of Object.entries(validationRules)) {
    const fieldValue = formData[fieldName];
    const fieldResult = new ValidationResult();
    
    // Apply each validation rule
    for (const rule of rules) {
      let ruleResult;
      
      switch (rule.type) {
        case 'required':
          ruleResult = validateRequired(fieldValue, rule.fieldName || fieldName);
          break;
        case 'length':
          ruleResult = validateTextLength(
            fieldValue,
            rule.minLength,
            rule.maxLength,
            rule.fieldName || fieldName
          );
          break;
        case 'email':
          ruleResult = validateEmail(fieldValue);
          break;
        case 'url':
          ruleResult = validateURL(fieldValue);
          break;
        case 'file':
          ruleResult = validateFile(fieldValue, rule.options);
          break;
        case 'jobDescription':
          ruleResult = validateJobDescription(fieldValue);
          break;
        case 'custom':
          ruleResult = rule.validator(fieldValue, formData);
          break;
        default:
          continue;
      }
      
      // Merge rule result into field result
      fieldResult.errors = [...fieldResult.errors, ...ruleResult.errors];
      fieldResult.warnings = [...fieldResult.warnings, ...ruleResult.warnings];
    }
    
    fieldResult.isValid = fieldResult.errors.length === 0;
    fieldResults[fieldName] = fieldResult;
    
    // Merge field result into overall result
    result.errors = [...result.errors, ...fieldResult.errors];
    result.warnings = [...result.warnings, ...fieldResult.warnings];
  }
  
  result.isValid = result.errors.length === 0;
  result.metadata.fieldResults = fieldResults;
  
  return result;
}

/**
 * Sanitize text input to prevent XSS and other security issues
 */
export function sanitizeText(text) {
  if (!text || typeof text !== 'string') return '';
  
  return text
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .replace(/javascript:/gi, '') // Remove javascript: URLs
    .replace(/on\w+=/gi, '') // Remove event handlers
    .trim();
}

/**
 * Debounce validation for real-time validation
 */
export function createDebouncedValidator(validator, delay = 300) {
  let timeoutId;
  
  return function debouncedValidator(...args) {
    return new Promise((resolve) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        resolve(validator(...args));
      }, delay);
    });
  };
}

/**
 * Create validation schema for common form patterns
 */
export const ValidationSchemas = {
  resumeUpload: {
    file: [
      { type: 'required' },
      { type: 'file', options: { fieldName: 'Resume file' } }
    ]
  },
  
  jobDescriptionForm: {
    jobDescription: [
      { type: 'jobDescription' }
    ]
  },
  
  analysisForm: {
    file: [
      { type: 'required' },
      { type: 'file', options: { fieldName: 'Resume file' } }
    ],
    jobDescription: [
      { type: 'jobDescription' }
    ]
  },
  
  contactForm: {
    name: [
      { type: 'required' },
      { type: 'length', maxLength: TextValidation.NAME_MAX_LENGTH }
    ],
    email: [
      { type: 'required' },
      { type: 'email' },
      { type: 'length', maxLength: TextValidation.EMAIL_MAX_LENGTH }
    ]
  }
};

export default {
  ValidationResult,
  ValidationErrorTypes,
  FileValidation,
  TextValidation,
  validateRequired,
  validateTextLength,
  validateNotWhitespaceOnly,
  validateEmail,
  validateURL,
  validateFile,
  validateJobDescription,
  validateForm,
  sanitizeText,
  createDebouncedValidator,
  ValidationSchemas
};