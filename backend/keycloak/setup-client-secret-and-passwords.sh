#!/bin/bash

# Wait for Keycloak to be fully up
until $(curl --output /dev/null --silent --head --fail http://keycloak:8080); do
    echo "Waiting for Keycloak to start..."
    sleep 5
done

# Get an admin token
TOKEN=$(curl -s \
  -d "client_id=admin-cli" \
  -d "username=admin" \
  -d "password=p" \
  -d "grant_type=password" \
  "http://keycloak:8080/realms/master/protocol/openid-connect/token" | jq -r '.access_token')

# Set client secret for a specific client
curl -X POST "http://keycloak:8080/admin/realms/nest/clients/nest/client-secret" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "value": "k2NKsXJ9pwuSyBMqKzWWLcYlJaZ7q1qb"
  }'

# Function to create or reset user password
create_or_reset_user() {
  local username=$1
  local password=$2

  # Check if the user exists
  USER_ID=$(curl -s -X GET "http://keycloak:8080/admin/realms/nest/users?username=$username" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" | jq -r '.[0].id')

  if [ "$USER_ID" == "null" ]; then
    echo "User $username not found, creating..."
    # Create the user
    curl -s -X POST "http://keycloak:8080/admin/realms/nest/users" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "username": "'"$username"'",
        "enabled": true,
        "credentials": [{
          "type": "password",
          "value": "'"$password"'",
          "temporary": false
        }]
      }'
    USER_ID=$(curl -s -X GET "http://keycloak:8080/admin/realms/nest/users?username=$username" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" | jq -r '.[0].id')
  else
    echo "User $username found, resetting password..."
    # Reset the user's password
    curl -X PUT "http://keycloak:8080/admin/realms/nest/users/$USER_ID/reset-password" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "type": "password",
        "temporary": false,
        "value": "'"$password"'"
      }'
  fi
}

# Create or reset passwords for users
create_or_reset_user "admin" "p"
create_or_reset_user "user" "p"

echo "Client secret and user passwords configured!"
