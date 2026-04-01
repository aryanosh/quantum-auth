import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import PrivateRoute from '../components/PrivateRoute';

jest.mock('../auth/AuthContext', () => ({
  useAuth: jest.fn()
}));

function LoginStub() {
  return <div>LOGIN_PAGE</div>;
}

test('redirects to /login when not authenticated', () => {
  const { useAuth } = require('../auth/AuthContext'); // eslint-disable-line global-require
  useAuth.mockReturnValue({ isAuthenticated: false, status: 'ready' });

  render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <Routes>
        <Route path="/login" element={<LoginStub />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <div>DASHBOARD</div>
            </PrivateRoute>
          }
        />
      </Routes>
    </MemoryRouter>
  );

  expect(screen.getByText('LOGIN_PAGE')).toBeInTheDocument();
});

