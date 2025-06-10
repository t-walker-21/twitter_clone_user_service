#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Set environment variables
export APP_ENV="test"
export SQL_URL_STRING="sqlite:///memory"
export JWT_SECRET="your_jwt_secret"  # Replace with your actual JWT secret

# Start the Uvicorn server in the background
uvicorn src.app:app --host 127.0.0.1 --port 8000 &
UVICORN_PID=$!

# Wait for the server to start
sleep 3

# Define the base URL
BASE_URL="http://127.0.0.1:8000/users"

# Create a test user for authentication
curl -X POST "$BASE_URL/users" -H "Content-Type: application/json" -d '{
  "first_name": "John",
  "last_name": "Doe",
  "username": "johndoe",
  "email": "johndoe@example.com",
  "password": "password123",
  "date_of_birth": "1990-01-01"
}' -w "\nStatus: %{http_code}\n" -o /dev/null

# Log in to get the JWT token
JWT_TOKEN=$(curl -X POST "$BASE_URL/login/" -H "Content-Type: application/json" -d '{
  "email_address": "johndoe@example.com",
  "password": "password123"
}' | jq -r '.jwt_token')

# Add the Authorization header
AUTH_HEADER="Authorization: Bearer $JWT_TOKEN"

# Test endpoints
echo "Testing GET /users/1"
curl -X GET "$BASE_URL/users/1" -H "$AUTH_HEADER" -w "\nStatus: %{http_code}\n" -o /dev/null

echo "Testing POST /users"
curl -X POST "$BASE_URL/users" -H "Content-Type: application/json" -H "$AUTH_HEADER" -d '{
  "first_name": "Jane",
  "last_name": "Doe",
  "username": "janedoe",
  "email": "janedoe@example.com",
  "password": "password123",
  "date_of_birth": "1992-02-02"
}' -w "\nStatus: %{http_code}\n" -o /dev/null

echo "Testing PUT /users/1"
curl -X PUT "$BASE_URL/users/1" -H "Content-Type: application/json" -H "$AUTH_HEADER" -d '{
  "first_name": "John",
  "last_name": "Smith",
  "username": "johnsmith",
  "email": "johnsmith@example.com",
  "password": "password123",
  "date_of_birth": "1990-01-01"
}' -w "\nStatus: %{http_code}\n" -o /dev/null

echo "Testing DELETE /users/1"
curl -X DELETE "$BASE_URL/users/1" -H "$AUTH_HEADER" -w "\nStatus: %{http_code}\n" -o /dev/null

# Stop the Uvicorn server
kill $UVICORN_PID
wait $UVICORN_PID 2>/dev/null || true

echo "Integration tests completed successfully."