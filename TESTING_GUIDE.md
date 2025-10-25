# Testing Guide for TranslatAR Google OAuth Integration

This guide explains how to run all tests for the Google OAuth integration.

## Prerequisites

### Backend Tests
- Python 3.11+
- Docker and Docker Compose
- Backend dependencies installed

### Web Portal Tests
- Node.js 18+
- npm or yarn

### Unity Tests
- Unity Editor 2022.3.62f1 or later
- Unity Test Framework package

## Running Tests

### 1. Backend Tests

```bash
# Install dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run all backend tests
python run_tests.py

# Or run specific test suites
python -m pytest tests/test_auth_controller.py -v
python -m pytest tests/test_auth_integration.py -v
```

### 2. Web Portal Tests

```bash
# Install dependencies
cd web-portal
npm install

# Run tests
npm test

# Build verification
npm run build
```

### 3. Unity Tests

#### Option A: Using Unity Editor (Recommended)
1. Open Unity Editor
2. Open the project in `unity/` directory
3. Go to `Window > General > Test Runner`
4. Click `Run All` in the Test Runner window

#### Option B: Using Command Line (macOS/Windows)
```bash
# From project root
./scripts/run_unity_tests.sh
```

#### Option C: Using Test Scripts
```bash
# Run all tests
./scripts/run_all_tests.sh

# Run specific test suites
./scripts/run_unit_tests.sh
./scripts/run_integration_tests.sh
```

## Test Coverage

### Backend Tests
- **Unit Tests**: `test_auth_controller.py`
  - Google OAuth login flow
  - Token verification
  - User management
  - Error handling

- **Integration Tests**: `test_auth_integration.py`
  - Complete OAuth flow
  - Database integration
  - JWT token lifecycle

### Unity Tests
- **GoogleSignInManagerTest.cs**: Core authentication manager
- **GoogleSignInConfigTest.cs**: Configuration management
- **GoogleSignInUITest.cs**: UI component testing
- **TestRunner.cs**: Integration test runner

### Web Portal Tests
- **Component Tests**: React component testing
- **Build Verification**: TypeScript compilation
- **Integration Tests**: Authentication flow

## Troubleshooting

### Backend Test Issues
- Ensure MongoDB is running: `docker compose up -d mongodb`
- Check environment variables in `.env`
- Verify JWT secret is set

### Web Portal Test Issues
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check TypeScript configuration
- Verify all dependencies are installed

### Unity Test Issues
- Ensure Unity Test Framework package is installed
- Check Unity version compatibility
- Verify all scripts compile without errors
- Check for missing using statements

## Expected Results

### Successful Test Run
```
Backend Tests: PASSED
Web Portal Build: SUCCESS
Unity Tests: PASSED
All Tests: PASSED
```

### Test Output Examples
- Backend: Coverage reports and test results
- Web Portal: Build artifacts in `dist/` directory
- Unity: Test results in Unity Test Runner window

## Continuous Integration

For CI/CD pipelines, use the provided scripts:
- `scripts/run_all_tests.sh` - Runs all test suites
- `scripts/run_unit_tests.sh` - Backend unit tests only
- `scripts/run_integration_tests.sh` - Backend integration tests only
- `scripts/run_unity_tests.sh` - Unity tests only

## Notes

- Unity tests require Unity Editor to be installed
- Backend tests require Docker for database services
- Web portal tests require Node.js environment
- All tests use placeholder credentials for security
