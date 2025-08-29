/**
 * FeedbackMessage Component for Resume Curator
 * 
 * Provides error messages, success feedback, and actionable content
 * as required by Requirements 7.3, 7.4, 1.6.
 */

import { useState, useEffect, useCallback } from 'react';
import {
    CheckCircleIcon,
    ExclamationTriangleIcon,
    InformationCircleIcon,
    XCircleIcon,
    XMarkIcon
} from '@heroicons/react/24/outline';

const FeedbackMessage = ({
    type = 'info', // 'success', 'error', 'warning', 'info'
    title,
    message,
    details = [],
    actions = [],
    dismissible = false,
    autoHide = false,
    autoHideDelay = 5000,
    onDismiss,
    className = ''
}) => {
    const [isVisible, setIsVisible] = useState(true);

    // Auto-hide functionality
    useEffect(() => {
        if (autoHide && autoHideDelay > 0) {
            const timer = setTimeout(() => {
                handleDismiss();
            }, autoHideDelay);
            return () => clearTimeout(timer);
        }
    }, [autoHide, autoHideDelay, handleDismiss]);

    // Handle dismiss
    const handleDismiss = useCallback(() => {
        setIsVisible(false);
        if (onDismiss) {
            onDismiss();
        }
    }, [onDismiss]);

    // Get icon based on type
    const getIcon = () => {
        switch (type) {
            case 'success':
                return <CheckCircleIcon className="h-5 w-5 text-green-400" />;
            case 'error':
                return <XCircleIcon className="h-5 w-5 text-red-400" />;
            case 'warning':
                return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />;
            default:
                return <InformationCircleIcon className="h-5 w-5 text-blue-400" />;
        }
    };

    // Get container classes
    const getContainerClasses = () => {
        const baseClasses = "rounded-md p-4 transition-all duration-300";

        switch (type) {
            case 'success':
                return `${baseClasses} bg-green-50 border border-green-200`;
            case 'error':
                return `${baseClasses} bg-red-50 border border-red-200`;
            case 'warning':
                return `${baseClasses} bg-yellow-50 border border-yellow-200`;
            default:
                return `${baseClasses} bg-blue-50 border border-blue-200`;
        }
    };

    // Get text color classes
    const getTextClasses = () => {
        switch (type) {
            case 'success':
                return 'text-green-800';
            case 'error':
                return 'text-red-800';
            case 'warning':
                return 'text-yellow-800';
            default:
                return 'text-blue-800';
        }
    };

    // Get secondary text color classes
    const getSecondaryTextClasses = () => {
        switch (type) {
            case 'success':
                return 'text-green-700';
            case 'error':
                return 'text-red-700';
            case 'warning':
                return 'text-yellow-700';
            default:
                return 'text-blue-700';
        }
    };

    // Get button classes
    const getButtonClasses = (variant = 'primary') => {
        const baseClasses = "inline-flex items-center px-3 py-2 border text-sm leading-4 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors";

        if (variant === 'secondary') {
            switch (type) {
                case 'success':
                    return `${baseClasses} border-green-300 text-green-700 bg-green-100 hover:bg-green-200 focus:ring-green-500`;
                case 'error':
                    return `${baseClasses} border-red-300 text-red-700 bg-red-100 hover:bg-red-200 focus:ring-red-500`;
                case 'warning':
                    return `${baseClasses} border-yellow-300 text-yellow-700 bg-yellow-100 hover:bg-yellow-200 focus:ring-yellow-500`;
                default:
                    return `${baseClasses} border-blue-300 text-blue-700 bg-blue-100 hover:bg-blue-200 focus:ring-blue-500`;
            }
        }

        // Primary button
        switch (type) {
            case 'success':
                return `${baseClasses} border-transparent text-white bg-green-600 hover:bg-green-700 focus:ring-green-500`;
            case 'error':
                return `${baseClasses} border-transparent text-white bg-red-600 hover:bg-red-700 focus:ring-red-500`;
            case 'warning':
                return `${baseClasses} border-transparent text-white bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500`;
            default:
                return `${baseClasses} border-transparent text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500`;
        }
    };

    if (!isVisible) {
        return null;
    }

    return (
        <div className={`${getContainerClasses()} ${className}`}>
            <div className="flex">
                {/* Icon */}
                <div className="flex-shrink-0">
                    {getIcon()}
                </div>

                {/* Content */}
                <div className="ml-3 flex-1">
                    {/* Title */}
                    {title && (
                        <h3 className={`text-sm font-medium ${getTextClasses()}`}>
                            {title}
                        </h3>
                    )}

                    {/* Message */}
                    {message && (
                        <div className={`${title ? 'mt-2' : ''} text-sm ${getSecondaryTextClasses()}`}>
                            <p>{message}</p>
                        </div>
                    )}

                    {/* Details list */}
                    {details.length > 0 && (
                        <div className={`${title || message ? 'mt-2' : ''} text-sm ${getSecondaryTextClasses()}`}>
                            <ul className="list-disc list-inside space-y-1">
                                {details.map((detail, index) => (
                                    <li key={index}>{detail}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Actions */}
                    {actions.length > 0 && (
                        <div className={`${title || message || details.length > 0 ? 'mt-4' : ''} flex space-x-3`}>
                            {actions.map((action, index) => (
                                <button
                                    key={index}
                                    type="button"
                                    onClick={action.onClick}
                                    disabled={action.disabled}
                                    className={`${getButtonClasses(action.variant)} ${action.disabled ? 'opacity-50 cursor-not-allowed' : ''
                                        }`}
                                >
                                    {action.icon && (
                                        <action.icon className="h-4 w-4 mr-1.5" />
                                    )}
                                    {action.label}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Dismiss button */}
                {dismissible && (
                    <div className="ml-auto pl-3">
                        <div className="-mx-1.5 -my-1.5">
                            <button
                                type="button"
                                onClick={handleDismiss}
                                className={`inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors ${type === 'success'
                                        ? 'text-green-500 hover:bg-green-100 focus:ring-green-600'
                                        : type === 'error'
                                            ? 'text-red-500 hover:bg-red-100 focus:ring-red-600'
                                            : type === 'warning'
                                                ? 'text-yellow-500 hover:bg-yellow-100 focus:ring-yellow-600'
                                                : 'text-blue-500 hover:bg-blue-100 focus:ring-blue-600'
                                    }`}
                            >
                                <span className="sr-only">Dismiss</span>
                                <XMarkIcon className="h-5 w-5" />
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

// Predefined message types for common scenarios
export const SuccessMessage = (props) => (
    <FeedbackMessage type="success" {...props} />
);

export const ErrorMessage = (props) => (
    <FeedbackMessage type="error" {...props} />
);

export const WarningMessage = (props) => (
    <FeedbackMessage type="warning" {...props} />
);

export const InfoMessage = (props) => (
    <FeedbackMessage type="info" {...props} />
);

export default FeedbackMessage;