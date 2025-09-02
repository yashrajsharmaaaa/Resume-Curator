import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import FileUpload from '../FileUpload';

// Mock file for testing
const createMockFile = (name = 'test.pdf', size = 1024, type = 'application/pdf') => {
  return new File(['test content'], name, { type, size });
};

describe('FileUpload Component', () => {
  const mockOnFileSelect = jest.fn();

  beforeEach(() => {
    mockOnFileSelect.mockClear();
  });

  test('renders upload area with correct text', () => {
    render(<FileUpload onFileSelect={mockOnFileSelect} />);
    
    expect(screen.getByText('Upload your resume')).toBeInTheDocument();
    expect(screen.getByText('Drag and drop your PDF file here, or click to browse')).toBeInTheDocument();
    expect(screen.getByText('PDF files only, up to 10MB')).toBeInTheDocument();
  });

  test('shows loading state when uploading', () => {
    render(<FileUpload onFileSelect={mockOnFileSelect} isUploading={true} />);
    
    expect(screen.getByText('Uploading your resume...')).toBeInTheDocument();
  });

  test('displays error message when provided', () => {
    const errorMessage = 'File too large';
    render(<FileUpload onFileSelect={mockOnFileSelect} error={errorMessage} />);
    
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  test('calls onFileSelect with valid PDF file', () => {
    render(<FileUpload onFileSelect={mockOnFileSelect} />);
    
    const fileInput = document.getElementById('file-input');
    const validFile = createMockFile('resume.pdf', 1024, 'application/pdf');
    
    fireEvent.change(fileInput, { target: { files: [validFile] } });
    
    expect(mockOnFileSelect).toHaveBeenCalledWith(validFile, null);
  });

  test('rejects non-PDF files', () => {
    render(<FileUpload onFileSelect={mockOnFileSelect} />);
    
    const fileInput = document.getElementById('file-input');
    const invalidFile = createMockFile('document.docx', 1024, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
    
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });
    
    expect(mockOnFileSelect).toHaveBeenCalledWith(null, 'Please upload a PDF file only.');
  });

  test('rejects files larger than 10MB', () => {
    render(<FileUpload onFileSelect={mockOnFileSelect} />);
    
    const fileInput = document.getElementById('file-input');
    const largeFile = createMockFile('large.pdf', 11 * 1024 * 1024, 'application/pdf'); // 11MB
    
    fireEvent.change(fileInput, { target: { files: [largeFile] } });
    
    expect(mockOnFileSelect).toHaveBeenCalledWith(null, 'File size must be less than 10MB.');
  });

  test('handles drag and drop', () => {
    render(<FileUpload onFileSelect={mockOnFileSelect} />);
    
    const dropZone = screen.getByText('Upload your resume').closest('div').parentElement;
    const validFile = createMockFile('resume.pdf', 1024, 'application/pdf');
    
    fireEvent.drop(dropZone, {
      dataTransfer: {
        files: [validFile]
      }
    });
    
    expect(mockOnFileSelect).toHaveBeenCalledWith(validFile, null);
  });
});