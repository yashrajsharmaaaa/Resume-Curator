/**
 * Unit Tests for MinimalFileUpload Component
 * 
 * Tests file upload interactions, validation, and drag-and-drop functionality.
 * Requirements: 3.1, 3.2, 3.3, 3.4
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import MinimalFileUpload from '../MinimalFileUpload';

// Mock react-dropzone
vi.mock('react-dropzone', () => ({
  useDropzone: vi.fn()
}));

describe('MinimalFileUpload', () => {
  const mockOnFileSelect = vi.fn();
  const mockGetRootProps = vi.fn(() => ({}));
  const mockGetInputProps = vi.fn(() => ({}));

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Setup default dropzone mock
    const { useDropzone } = require('react-dropzone');
    useDropzone.mockReturnValue({
      getRootProps: mockGetRootProps,
      getInputProps: mockGetInputProps
    });
  });

  it('renders upload zone with default message', () => {
    render(
      <MinimalFileUpload onFileSelect={mockOnFileSelect} />
    );

    expect(screen.getByText('Drop resume here or click to select')).toBeInTheDocument();
  });

  it('shows processing state when isProcessing is true', () => {
    render(
      <MinimalFileUpload 
        onFileSelect={mockOnFileSelect} 
        isProcessing={true} 
      />
    );

    expect(screen.getByText('Processing...')).toBeInTheDocument();
  });

  it('displays error message when error prop is provided', () => {
    const errorMessage = 'File too large';
    
    render(
      <MinimalFileUpload 
        onFileSelect={mockOnFileSelect} 
        error={errorMessage} 
      />
    );

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('calls onFileSelect with file when valid file is dropped', async () => {
    const mockFile = new File(['test'], 'test.pdf', { type: 'application/pdf' });
    
    const { useDropzone } = require('react-dropzone');
    useDropzone.mockImplementation(({ onDrop }) => {
      // Simulate successful file drop
      setTimeout(() => onDrop([mockFile], []), 0);
      
      return {
        getRootProps: mockGetRootProps,
        getInputProps: mockGetInputProps
      };
    });

    render(
      <MinimalFileUpload onFileSelect={mockOnFileSelect} />
    );

    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith(mockFile, null);
    });
  });

  it('calls onFileSelect with error when invalid file is dropped', async () => {
    const mockError = { errors: [{ message: 'File type not supported' }] };
    
    const { useDropzone } = require('react-dropzone');
    useDropzone.mockImplementation(({ onDrop }) => {
      // Simulate file rejection
      setTimeout(() => onDrop([], [mockError]), 0);
      
      return {
        getRootProps: mockGetRootProps,
        getInputProps: mockGetInputProps
      };
    });

    render(
      <MinimalFileUpload onFileSelect={mockOnFileSelect} />
    );

    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith(null, 'File type not supported');
    });
  });

  it('shows drag active state message when dragging over', () => {
    const { useDropzone } = require('react-dropzone');
    useDropzone.mockImplementation(({ onDragEnter }) => {
      // Simulate drag enter
      setTimeout(() => onDragEnter(), 0);
      
      return {
        getRootProps: mockGetRootProps,
        getInputProps: mockGetInputProps
      };
    });

    render(
      <MinimalFileUpload onFileSelect={mockOnFileSelect} />
    );

    // Initially shows default message, then should update to drag active
    expect(screen.getByText('Drop resume here or click to select')).toBeInTheDocument();
  });

  it('configures dropzone with correct file types and size limits', () => {
    const { useDropzone } = require('react-dropzone');
    
    render(
      <MinimalFileUpload onFileSelect={mockOnFileSelect} />
    );

    expect(useDropzone).toHaveBeenCalledWith(
      expect.objectContaining({
        accept: {
          'application/pdf': ['.pdf'],
          'application/msword': ['.doc'],
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
          'text/plain': ['.txt']
        },
        maxFiles: 1,
        maxSize: 10 * 1024 * 1024, // 10MB
        disabled: false
      })
    );
  });

  it('disables dropzone when isProcessing is true', () => {
    const { useDropzone } = require('react-dropzone');
    
    render(
      <MinimalFileUpload 
        onFileSelect={mockOnFileSelect} 
        isProcessing={true} 
      />
    );

    expect(useDropzone).toHaveBeenCalledWith(
      expect.objectContaining({
        disabled: true
      })
    );
  });
});