import React from 'react';
import { render, screen } from '@testing-library/react';
import LoadingSpinner from '../LoadingSpinner';

describe('LoadingSpinner Component', () => {
  test('renders spinner with default size', () => {
    render(<LoadingSpinner data-testid="spinner" />);
    const spinner = screen.getByTestId('spinner');
    expect(spinner).toHaveClass('w-8', 'h-8');
  });

  test('applies correct size classes', () => {
    render(<LoadingSpinner size="lg" data-testid="spinner" />);
    const spinner = screen.getByTestId('spinner');
    expect(spinner).toHaveClass('w-12', 'h-12');
  });

  test('has spinning animation', () => {
    render(<LoadingSpinner data-testid="spinner" />);
    const spinner = screen.getByTestId('spinner');
    expect(spinner).toHaveClass('animate-spin');
  });
});