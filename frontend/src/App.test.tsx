import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders mids web title', () => {
  render(<App />);
  const titleElement = screen.getByText(/mids-web/i);
  expect(titleElement).toBeInTheDocument();
});
