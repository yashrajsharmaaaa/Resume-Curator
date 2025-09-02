import React from 'react';
import { render, screen } from '@testing-library/react';
import Card from '../Card';

describe('Card Component', () => {
  test('renders card with children', () => {
    render(
      <Card>
        <p>Card content</p>
      </Card>
    );
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  test('applies shadow by default', () => {
    render(<Card data-testid="card">Content</Card>);
    const card = screen.getByTestId('card');
    expect(card).toHaveClass('shadow-sm');
  });

  test('removes shadow when shadow prop is false', () => {
    render(<Card shadow={false} data-testid="card">Content</Card>);
    const card = screen.getByTestId('card');
    expect(card).not.toHaveClass('shadow-sm');
  });

  test('applies correct padding classes', () => {
    render(<Card padding="lg" data-testid="card">Content</Card>);
    const card = screen.getByTestId('card');
    expect(card).toHaveClass('p-8');
  });
});