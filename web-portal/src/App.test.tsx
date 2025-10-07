import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import App from './App';

// We need to tell TypeScript about the fetchMock global
import { vi } from 'vitest';
declare var fetchMock: typeof vi & { mockResponseOnce: (body: string, init?: ResponseInit) => void };


describe('App', () => {
  // Reset mocks before each test
  beforeEach(() => {
    fetchMock.resetMocks();
  });

  it('should render the main heading and loading state initially', () => {
    render(<App />);
    expect(screen.getByText(/TranslatAR Web Portal/i)).toBeInTheDocument();
    expect(screen.getByText(/Loading history.../i)).toBeInTheDocument();
  });

  it('should display the translation history on successful fetch', async () => {
    // Mock the API response
    const mockHistory = [
      { _id: '1', original_text: 'Hello', translated_text: 'Hola', source_lang: 'en', target_lang: 'es', timestamp: '' },
      { _id: '2', original_text: 'Goodbye', translated_text: 'Adiós', source_lang: 'en', target_lang: 'es', timestamp: '' },
    ];
    fetchMock.mockResponseOnce(JSON.stringify({ history: mockHistory }));

    render(<App />);

    // Wait for the component to update after the fetch
    await waitFor(() => {
      // The "Loading..." text should be gone
      expect(screen.queryByText(/Loading history.../i)).not.toBeInTheDocument();
    });
    
    // Check that the mock data is displayed
    expect(screen.getByText(/Hello/i)).toBeInTheDocument();
    expect(screen.getByText(/Adiós/i)).toBeInTheDocument();
  });

  it('should display an error message if the fetch fails', async () => {
    // Mock a network error
    fetchMock.mockReject(new Error('API is down'));

    render(<App />);
    
    // Wait for the error message to appear
    const errorMessage = await screen.findByText(/Failed to load translation history./i);
    expect(errorMessage).toBeInTheDocument();
    expect(screen.queryByText(/Loading history.../i)).not.toBeInTheDocument();
  });
});
