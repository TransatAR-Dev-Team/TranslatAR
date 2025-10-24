#!/bin/bash

echo "🧪 Testing TranslatAR Google OAuth Integration"
echo "=============================================="

# Test 1: Check if services are running
echo "1. Checking service status..."
backend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
web_portal_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173)

if [ "$backend_status" = "200" ]; then
    echo "   ✅ Backend service is running (http://localhost:8000)"
else
    echo "   ❌ Backend service is not responding"
    exit 1
fi

if [ "$web_portal_status" = "200" ]; then
    echo "   ✅ Web portal is running (http://localhost:5173)"
else
    echo "   ❌ Web portal is not responding"
    exit 1
fi

# Test 2: Check Google OAuth endpoint
echo "2. Testing Google OAuth endpoint..."
oauth_response=$(curl -s http://localhost:8000/auth/google)
if echo "$oauth_response" | grep -q "auth_url"; then
    echo "   ✅ Google OAuth endpoint is working"
    echo "   📋 OAuth URL: $(echo "$oauth_response" | jq -r '.auth_url')"
else
    echo "   ❌ Google OAuth endpoint failed"
    echo "   Response: $oauth_response"
    exit 1
fi

# Test 3: Check environment variables in backend
echo "3. Checking backend environment variables..."
env_check=$(docker exec backend printenv | grep GOOGLE)
if echo "$env_check" | grep -q "GOOGLE_CLIENT_ID=861587845879"; then
    echo "   ✅ Google Client ID is properly configured"
else
    echo "   ❌ Google Client ID is missing or incorrect"
    echo "   Current: $env_check"
    exit 1
fi

# Test 4: Check JWT secret
jwt_check=$(docker exec backend printenv | grep JWT_SECRET)
if echo "$jwt_check" | grep -q "JWT_SECRET=314c02a1d4c1a7d184dead35e3a69adc62947d7049778d7c5685a233fd8b75d8"; then
    echo "   ✅ JWT Secret is properly configured"
else
    echo "   ❌ JWT Secret is missing or incorrect"
    echo "   Current: $jwt_check"
    exit 1
fi

# Test 5: Check callback endpoint
echo "4. Testing callback endpoint..."
callback_response=$(curl -s "http://localhost:8000/auth/google/callback?code=test")
if echo "$callback_response" | grep -q "Failed to obtain access token"; then
    echo "   ✅ Callback endpoint is working (expected error with test code)"
else
    echo "   ❌ Callback endpoint failed"
    echo "   Response: $callback_response"
    exit 1
fi

# Test 6: Check web portal can load
echo "5. Testing web portal loading..."
portal_content=$(curl -s http://localhost:5173)
if echo "$portal_content" | grep -q "TranslatAR"; then
    echo "   ✅ Web portal loads successfully"
else
    echo "   ❌ Web portal failed to load"
    exit 1
fi

echo ""
echo "🎉 All tests passed! Google OAuth integration is working correctly."
echo ""
echo "📱 You can now test the login functionality by:"
echo "   1. Opening http://localhost:5173 in your browser"
echo "   2. Clicking the 'Sign in with Google' button in the top right"
echo "   3. Completing the Google OAuth flow"
echo ""
echo "🔗 Additional endpoints:"
echo "   - Web Portal: http://localhost:5173"
echo "   - Backend API Docs: http://localhost:8000/docs"
echo "   - Google OAuth: http://localhost:8000/auth/google"


