import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Login from '../components/Login';

jest.mock('../auth/AuthContext', () => ({
  useAuth: jest.fn()
}));

jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => jest.fn(),
    useLocation: () => ({ state: null })
  };
});

test('login form renders and requires fields', async () => {
  const { useAuth } = require('../auth/AuthContext'); // eslint-disable-line global-require
  useAuth.mockReturnValue({
    login: jest.fn(async () => ({ success: false, message: 'Invalid username or password' })),
    status: 'ready'
  });

  render(<Login />);

  expect(screen.getByText(/Quantum-Secure Login/i)).toBeInTheDocument();
  const username = screen.getByLabelText(/Username/i);
  const password = screen.getByLabelText(/Password/i);
  expect(username).toBeInTheDocument();
  expect(password).toBeInTheDocument();

  // Browser validation is not triggered in jsdom, but required attributes should exist.
  expect(username).toHaveAttribute('required');
  expect(password).toHaveAttribute('required');
});

test('submitting calls auth.login with typed credentials', async () => {
  const loginMock = jest.fn(async () => ({ success: false, message: 'Invalid username or password' }));
  const { useAuth } = require('../auth/AuthContext'); // eslint-disable-line global-require
  useAuth.mockReturnValue({ login: loginMock, status: 'ready' });

  render(<Login />);
  const user = userEvent.setup();

  await user.type(screen.getByLabelText(/Username/i), 'alice');
  await user.type(screen.getByLabelText(/Password/i), 'SecurePass123');
  await user.click(screen.getByRole('button', { name: /login/i }));

  expect(loginMock).toHaveBeenCalledWith({ username: 'alice', password: 'SecurePass123' });
});

