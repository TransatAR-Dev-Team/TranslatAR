#!/bin/bash
# A script to test the OAuth 2.0 device flow using curl.

set -e # Exit immediately if a command exits with a non-zero status.

# --- Step 1: Start the device flow to get the codes ---
echo "🚀 Starting device flow..."
echo ""

# Make the request and capture the JSON response
start_response=$(curl -s -X POST http://localhost:8000/api/auth/device/start)

# Check if we got a valid JSON response with a device_code
if ! echo "$start_response" | jq -e '.device_code' > /dev/null; then
    echo "❌ ERROR: Failed to start device flow. Server response:"
    echo "$start_response" | jq .
    exit 1
fi

# Extract the codes using jq
device_code=$(echo "$start_response" | jq -r '.device_code')
user_code=$(echo "$start_response" | jq -r '.user_code')
verification_url=$(echo "$start_response" | jq -r '.verification_url')
interval=$(echo "$start_response" | jq -r '.interval') # Google's recommended polling interval

# --- Step 2: Display instructions for the manual browser part ---
echo "✅ Received codes from the server."
echo "--------------------------------------------------------"
echo "ACTION REQUIRED:"
echo "1. Open this URL in your browser: $verification_url"
echo "2. Enter this code when prompted: $user_code"
echo "3. Complete the login with your Google account."
echo "--------------------------------------------------------"
echo ""
echo "Waiting for you to log in. Now polling the server every $interval seconds..."


# --- Step 3: Poll the backend until the login is complete ---
while true; do
  # Make the polling request
  poll_response=$(curl -s -X POST http://localhost:8000/api/auth/device/poll \
    -H "Content-Type: application/json" \
    -d "{\"device_code\": \"$device_code\"}")

  # Extract the status
  status=$(echo "$poll_response" | jq -r '.status')

  if [ "$status" = "completed" ]; then
    echo -e "\n\n✅ Login successful! Received application access token:"
    echo "$poll_response" | jq .
    break
  elif [ "$status" != "authorization_pending" ]; then
    echo -e "\n\n❌ Flow failed or expired. Status: $status"
    echo "$poll_response" | jq .
    break
  else
    # Print a dot as a progress indicator so the user knows it's working
    echo -n "."
    sleep "$interval"
  fi
done
