import "@testing-library/jest-dom";
import createFetchMock from "vitest-fetch-mock";
import { vi } from "vitest";

const fetchMocker = createFetchMock(vi);

// sets globalThis.fetch and globalThis.fetchMock to our mock
fetchMocker.enableMocks();

// Hide console errors from failed fetches in tests
vi.spyOn(console, "error").mockImplementation(() => {});
