import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import App from './App';

// We need to declare fetchMock for TypeScript
declare var fetchMock: {
  resetMocks: () => void;
  mockResponseOnce: (body: string, init?: ResponseInit) => void;
  mockReject: (error: any) => void;
  mockResponse?: (body: string, init?: ResponseInit) => void;
  [key: string]: any;
};


describe('App Component', () => {
  // Reset mocks before each test runs
  beforeEach(() => {
    fetchMock.resetMocks();
    vi.unstubAllEnvs(); // Ensure no env stubs bleed between suites
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


describe('App Component with Environment Variables', () => {
  beforeEach(() => {
    fetchMock.resetMocks();
    vi.unstubAllEnvs();
  });

  it('should use the default API proxy target when VITE_API_PROXY_TARGET is not set', async () => {
    // Mock the API response
    const mockHistory = [{ _id: '1', original_text: 'Hello', translated_text: 'Hola', source_lang: 'en', target_lang: 'es', timestamp: new Date().toISOString() }];
    fetchMock.mockResponseOnce(JSON.stringify({ history: mockHistory }));

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/Hello/i)).toBeInTheDocument();
    });

    // Assert that fetch was called with the default URL
    expect(fetchMock).toHaveBeenCalledWith('/api/history');
  });

  it('should use the API proxy target from VITE_API_PROXY_TARGET when it is set', async () => {
    vi.stubEnv('VITE_API_PROXY_TARGET', 'http://test-backend:8000');

    // Mock the API response
    const mockHistory = [{ _id: '1', original_text: 'Hello', translated_text: 'Hola', source_lang: 'en', target_lang: 'es', timestamp: new Date().toISOString() }];
    fetchMock.mockResponseOnce(JSON.stringify({ history: mockHistory }));

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/Hello/i)).toBeInTheDocument();
    });

    // Assert that fetch was called with the overridden URL
    expect(fetchMock).toHaveBeenCalledWith('/api/history');
  });

  it('should handle errors when the API proxy target is invalid', async () => {
    vi.stubEnv('VITE_API_PROXY_TARGET', 'invalid-url');
    fetchMock.mockReject(new Error('Network error'));

    render(<App />);

    const errorMessage = await screen.findByText(/Failed to load translation history./i);
    expect(errorMessage).toBeInTheDocument();
  });
});
