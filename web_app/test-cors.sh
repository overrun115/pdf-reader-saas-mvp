#!/bin/bash

# CORS Configuration Test Script
echo "🔍 Testing CORS configuration..."
echo "=================================="

# Test 1: Health endpoint with GET
echo "1. Testing GET /api/health"
curl -i -X GET "http://127.0.0.1:8001/api/health" \
  -H "Origin: http://localhost:3000" \
  -H "Accept: application/json"
echo -e "\n"

# Test 2: CORS test endpoint with GET
echo "2. Testing GET /api/cors-test"
curl -i -X GET "http://127.0.0.1:8001/api/cors-test" \
  -H "Origin: http://localhost:3000" \
  -H "Accept: application/json"
echo -e "\n"

# Test 3: OPTIONS preflight request
echo "3. Testing OPTIONS preflight request"
curl -i -X OPTIONS "http://127.0.0.1:8001/api/auth/login" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type,authorization"
echo -e "\n"

# Test 4: Actual login POST request
echo "4. Testing POST /api/auth/login"
curl -i -X POST "http://127.0.0.1:8001/api/auth/login" \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"email": "admin@pdfextractor.com", "password": "admin123"}'
echo -e "\n"

echo "✅ CORS test completed!"
echo "Look for 'Access-Control-Allow-Origin' headers in the responses above."
