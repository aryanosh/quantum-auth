import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import WebcamCapture from '../components/WebcamCapture';

function makeStream() {
  return {
    getTracks: () => [{ stop: jest.fn() }]
  };
}

test('renders webcam capture UI and requests media', async () => {
  const getUserMedia = jest.fn().mockResolvedValue(makeStream());
  Object.defineProperty(global.navigator, 'mediaDevices', {
    value: { getUserMedia },
    configurable: true
  });

  render(<WebcamCapture onCapture={() => {}} onCancel={() => {}} />);

  expect(screen.getByRole('button', { name: /Capture Face/i })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();

  await waitFor(() => expect(getUserMedia).toHaveBeenCalled());
});

