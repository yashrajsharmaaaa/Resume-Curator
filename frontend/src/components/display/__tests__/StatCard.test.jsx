import React from 'react';
import { render, screen } from '@testing-library/react';
import StatCard from '../StatCard';

describe('StatCard Component', () => {
  test('renders basic stat card', () => {
    render(
      <StatCard
        title="Total Resumes"
        value="5"
        subtitle="Uploaded resumes"
      />
    );
    
    expect(screen.getByText('Total Resumes')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('Uploaded resumes')).toBeInTheDocument();
  });

  test('renders with icon', () => {
    const TestIcon = () => <div data-testid="test-icon">Icon</div>;
    
    render(
      <StatCard
        title="Test Stat"
        value="10"
        icon={<TestIcon />}
        color="green"
      />
    );
    
    expect(screen.getByTestId('test-icon')).toBeInTheDocument();
  });

  test('renders with upward trend', () => {
    render(
      <StatCard
        title="Score"
        value="85%"
        trend={{ direction: 'up', value: '+5%' }}
      />
    );
    
    expect(screen.getByText('+5%')).toBeInTheDocument();
  });

  test('renders with downward trend', () => {
    render(
      <StatCard
        title="Score"
        value="75%"
        trend={{ direction: 'down', value: '-3%' }}
      />
    );
    
    expect(screen.getByText('-3%')).toBeInTheDocument();
  });

  test('applies correct color classes', () => {
    render(
      <StatCard
        title="Test"
        value="100"
        color="purple"
        icon={<div data-testid="icon">Icon</div>}
      />
    );
    
    const iconContainer = screen.getByTestId('icon').parentElement;
    expect(iconContainer).toHaveClass('text-purple-600', 'bg-purple-100');
  });
});