/**
 * ValidationSummary Component for Resume Curator
 * 
 * Displays comprehensive validation errors and warnings with
 * specific messages and form submission prevention for invalid inputs.
 */

import { 
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

const ValidationSummary = ({
  errors = {},
  warnings = {},
  isValid = false,
  isValidating = false,
  showSuccessMessage = false,
  className = ''
}) => {
  const hasErrors = Object.keys(errors).some(key => errors[key]?.length > 0);
  const hasWarnings = Object.keys(warnings).some(key => warnings[key]?.length > 0);
  
  if (!hasErrors && !hasWarnings && !showSuccessMessage) {
    return null;
  }

  // Get all error messages
  const allErrors = Object.entries(errors)
    .filter(([, errorList]) => errorList?.length > 0)
    .flatMap(([field, errorList]) => 
      errorList.map(error => ({ field, message: error }))
    );

  // Get all warning messages
  const allWarnings = Object.entries(warnings)
    .filter(([, warningList]) => warningList?.length > 0)
    .flatMap(([field, warningList]) => 
      warningList.map(warning => ({ field, message: warning }))
    );

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Success Message */}
      {showSuccessMessage && isValid && !hasErrors && (
        <div className="rounded-md bg-green-50 p-4 border border-green-200">
          <div className="flex">
            <CheckCircleIcon className="h-5 w-5 text-green-400 flex-shrink-0" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800">
                Form is valid
              </h3>
              <p className="text-sm text-green-700 mt-1">
                All required fields have been filled out correctly.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Validation in Progress */}
      {isValidating && (
        <div className="rounded-md bg-blue-50 p-4 border border-blue-200">
          <div className="flex">
            <InformationCircleIcon className="h-5 w-5 text-blue-400 flex-shrink-0 animate-pulse" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">
                Validating form...
              </h3>
              <p className="text-sm text-blue-700 mt-1">
                Please wait while we validate your input.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error Messages */}
      {hasErrors && (
        <div className="rounded-md bg-red-50 p-4 border border-red-200">
          <div className="flex">
            <XCircleIcon className="h-5 w-5 text-red-400 flex-shrink-0" />
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-red-800">
                {allErrors.length === 1 ? 'There is 1 error' : `There are ${allErrors.length} errors`} with your submission
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <ul className="list-disc list-inside space-y-1">
                  {allErrors.map((error, index) => (
                    <li key={index} className="break-words">
                      <span className="font-medium capitalize">
                        {error.field === 'file' ? 'Resume file' : 
                         error.field === 'jobDescription' ? 'Job description' : 
                         error.field}:
                      </span>{' '}
                      {error.message}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="mt-3">
                <p className="text-xs text-red-600">
                  Please fix these errors before submitting the form.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Warning Messages */}
      {hasWarnings && !hasErrors && (
        <div className="rounded-md bg-yellow-50 p-4 border border-yellow-200">
          <div className="flex">
            <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400 flex-shrink-0" />
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-yellow-800">
                {allWarnings.length === 1 ? 'There is 1 warning' : `There are ${allWarnings.length} warnings`}
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <ul className="list-disc list-inside space-y-1">
                  {allWarnings.map((warning, index) => (
                    <li key={index} className="break-words">
                      <span className="font-medium capitalize">
                        {warning.field === 'file' ? 'Resume file' : 
                         warning.field === 'jobDescription' ? 'Job description' : 
                         warning.field}:
                      </span>{' '}
                      {warning.message}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="mt-3">
                <p className="text-xs text-yellow-600">
                  You can still submit the form, but addressing these warnings may improve your results.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Form Submission Prevention Notice */}
      {hasErrors && (
        <div className="rounded-md bg-gray-50 p-3 border border-gray-200">
          <div className="flex items-center">
            <InformationCircleIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
            <p className="ml-2 text-xs text-gray-600">
              Form submission is disabled until all errors are resolved.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ValidationSummary;