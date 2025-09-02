import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ResumeCard from '../ResumeCard';

const mockResume = {
  id: 1,
  fileName: 'test-resume.pdf',
  uploadDate: '2024-01-15',
  fileSize: 245760,
  score: 85,
  analysis: {
    keySkills: ['React', 'JavaScript', 'Node.js']
  }
};

describe('ResumeCard Component', () => {
  const mockOnClick = jest.fn();

  beforeEach(() => {
    mockOnClick.mockClear();
  });

  test('renders resume information correctly', () => {
    render(<ResumeCard resume={mockResume} onClick={mockOnClick} />);
    
    expect(screen.getByText('test-resume.pdf')).toBeInTheDocument();
    expect(screen.getByText('Uploaded: Jan 15, 2024')).toBeInTheDocument();
    expect(screen.getByText('Size: 240 KB')).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  test('displays key skills when available', () => {
    render(<ResumeCard resume={mockResume} onClick={mockOnClick} />);
    
    expect(screen.getByText('Key Skills Found:')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
    expect(screen.getByText('Node.js')).toBeInTheDocument();
  });

  test('shows correct score color for different ranges', () => {
    const highScoreResume = { ...mockResume, score: 95 };
    const { rerender } = render(<ResumeCard resume={highScoreResume} onClick={mockOnClick} />);
    
    let scoreElement = screen.getByText('95%');
    expect(scoreElement).toHaveClass('text-green-800');

    const lowScoreResume = { ...mockResume, score: 65 };
    rerender(<ResumeCard resume={lowScoreResume} onClick={mockOnClick} />);
    
    scoreElement = screen.getByText('65%');
    expect(scoreElement).toHaveClass('text-red-800');
  });

  test('calls onClick when card is clicked', () => {
    render(<ResumeCard resume={mockResume} onClick={mockOnClick} />);
    
    const card = screen.getByText('test-resume.pdf').closest('.cursor-pointer');
    fireEvent.click(card);
    
    expect(mockOnClick).toHaveBeenCalledWith(mockResume);
  });

  test('calls onClick when View Analysis button is clicked', () => {
    render(<ResumeCard resume={mockResume} onClick={mockOnClick} />);
    
    const viewButton = screen.getByText('View Analysis');
    fireEvent.click(viewButton);
    
    expect(mockOnClick).toHaveBeenCalledWith(mockResume);
  });

  test('renders without analysis data', () => {
    const resumeWithoutAnalysis = {
      ...mockResume,
      analysis: undefined
    };
    
    render(<ResumeCard resume={resumeWithoutAnalysis} onClick={mockOnClick} />);
    
    expect(screen.getByText('test-resume.pdf')).toBeInTheDocument();
    expect(screen.queryByText('Key Skills Found:')).not.toBeInTheDocument();
  });
});