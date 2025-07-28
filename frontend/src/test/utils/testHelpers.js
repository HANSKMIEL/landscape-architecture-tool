import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect } from 'vitest';

// Helper to setup user events
export const setupUser = () => userEvent.setup();

// Helper to wait for loading states to complete
export const waitForLoadingToFinish = async () => {
  await waitFor(() => {
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
  });
};

// Helper to fill form fields
export const fillForm = async (user, formData) => {
  for (const [fieldName, value] of Object.entries(formData)) {
    const field = screen.getByLabelText(new RegExp(fieldName, 'i'));
    await user.clear(field);
    await user.type(field, value);
  }
};

// Helper to submit forms
export const submitForm = async (user, buttonText = /submit/i) => {
  const submitButton = screen.getByRole('button', { name: buttonText });
  await user.click(submitButton);
};

// Helper to check if element is visible
export const expectElementToBeVisible = (element) => {
  expect(element).toBeInTheDocument();
  expect(element).toBeVisible();
};

// Helper to check loading states
export const expectLoadingState = () => {
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
};

// Helper to check error states
export const expectErrorMessage = (message) => {
  expect(screen.getByText(message)).toBeInTheDocument();
};

// Helper to check success states
export const expectSuccessMessage = (message) => {
  expect(screen.getByText(message)).toBeInTheDocument();
};