import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import App from './App';

// We need to declare fetchMock for TypeScript
declare var fetchMock: typeof vi & { 
  mockResponseOnce: (body: string, init?: ResponseInit) => void;
  resetAllMocks: () => void;
  mockReject: (error: Error) => void;
};


describe('App Component', () => {
  // Reset mocks before each test runs
  beforeEach(() => {
    fetchMock.resetAllMocks();
  });

  it('should render the main heading and show the initial loading state', () => {
    render(<App />);
    expect(screen.getByText(/TranslatAR Web Portal/i)).toBeInTheDocument();
    expect(screen.getByText(/Loading history.../i)).toBeInTheDocument();
  });

  it('should display the translation history after a successful fetch', async () => {
    // Mock the API response for history
    const mockHistory = [
      { _id: '1', original_text: 'Hello', translated_text: 'Hola', source_lang: 'en', target_lang: 'es', timestamp: new Date().toISOString() },
      { _id: '2', original_text: 'Goodbye', translated_text: 'Adiós', source_lang: 'en', target_lang: 'es', timestamp: new Date().toISOString() },
    ];
    fetchMock.mockResponseOnce(JSON.stringify({ history: mockHistory }));

    render(<App />);

    // Wait for the component to re-render after fetching data
    await waitFor(() => {
      // The "Loading..." text should disappear
      expect(screen.queryByText(/Loading history.../i)).not.toBeInTheDocument();
    });
    
    // Check that our mock data is now on the screen
    expect(screen.getByText(/Hello/i)).toBeInTheDocument();
    expect(screen.getByText(/Adiós/i)).toBeInTheDocument();
  });

  it('should display an error message if the fetch fails', async () => {
    // Mock a network error
    fetchMock.mockReject(new Error('API is unavailable'));

    render(<App />);
    
    // Wait for the error message to appear in the UI
    const errorMessage = await screen.findByText(/Failed to load translation history./i);
    expect(errorMessage).toBeInTheDocument();
    expect(screen.queryByText(/Loading history.../i)).not.toBeInTheDocument();
  });
});
