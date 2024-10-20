import time
import requests
import json

# Keycloak server URL and admin credentials
KEYCLOAK_SERVER_URL = "http://keycloak:8080"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "p"
REALM_NAME = "master"
NEST_REALM_NAME = "nest"
CLIENT_ID = "nest-client"
ADMIN_ROLE = "admin"
USER_ROLE = "user"

# Step 1: Get an admin token
def get_admin_token():
    url = f"{KEYCLOAK_SERVER_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"
    data = {
        "client_id": "admin-cli",
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "grant_type": "password"
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# Step 2: Set client secret for the 'nest-client'
def set_client_secret(token, client_secret_value):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Fetch client ID first
    clients_url = f"{KEYCLOAK_SERVER_URL}/admin/realms/{NEST_REALM_NAME}/clients"
    clients_response = requests.get(clients_url, headers=headers)
    clients_response.raise_for_status()
    clients = clients_response.json()

    nest_client_id = None
    for client in clients:
        if client["clientId"] == CLIENT_ID:
            nest_client_id = client["id"]
            break

    if nest_client_id is None:
        raise ValueError(f"Client '{CLIENT_ID}' not found in realm '{NEST_REALM_NAME}'")

    # Set the client secret
    secret_url = f"{KEYCLOAK_SERVER_URL}/admin/realms/{NEST_REALM_NAME}/clients/{nest_client_id}/client-secret"
    data = json.dumps({"value": client_secret_value})
    response = requests.post(secret_url, headers=headers, data=data)
    response.raise_for_status()

# Step 3: Create or reset user and set additional fields (firstName, lastName, email)
def create_or_reset_user(token, username, password, email, first_name, last_name):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Check if the user exists
    users_url = f"{KEYCLOAK_SERVER_URL}/admin/realms/{NEST_REALM_NAME}/users"
    params = {"username": username}
    users_response = requests.get(users_url, headers=headers, params=params)
    users_response.raise_for_status()
    users = users_response.json()

    if users:
        user_id = users[0]["id"]
        print(f"User {username} found, resetting password...")

        # Reset the user's password
        reset_url = f"{KEYCLOAK_SERVER_URL}/admin/realms/{NEST_REALM_NAME}/users/{user_id}/reset-password"
        password_data = {
            "type": "password",
            "temporary": False,
            "value": password
        }
        requests.put(reset_url, headers=headers, data=json.dumps(password_data))

        # Update user's details (email, firstName, lastName)
        update_url = f"{KEYCLOAK_SERVER_URL}/admin/realms/{NEST_REALM_NAME}/users/{user_id}"
        user_data = {
            "email": email,
            "firstName": first_name,
            "lastName": last_name
        }
        requests.put(update_url, headers=headers, data=json.dumps(user_data))

    else:
        print(f"User {username} not found, creating...")
        # Create the user
        create_url = f"{KEYCLOAK_SERVER_URL}/admin/realms/{NEST_REALM_NAME}/users"
        create_data = {
            "username": username,
            "enabled": True,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "credentials": [{
                "type": "password",
                "value": password,
                "temporary": False
            }]
        }
        users_response = requests.post(create_url, headers=headers, data=json.dumps(create_data))
        users_response.raise_for_status()
        user_id = users_response.json()["id"]

    return user_id

# Step 4: Assign role to user
def assign_client_role_to_user(token, user_id, client_role_name):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Get client roles
    clients_url = f"{KEYCLOAK_SERVER_URL}/admin/realms/{NEST_REALM_NAME}/clients"
    clients_response = requests.get(clients_url, headers=headers)
    clients_response.raise_for_status()
    clients = clients_response.json()

    client_id = None
    for client in clients:
        if client["clientId"] == CLIENT_ID:
            client_id = client["id"]
            break

    if not client_id:
        raise ValueError(f"Client '{CLIENT_ID}' not found in realm '{NEST_REALM_NAME}'")

    # Get role ID
    roles_url = f"{KEYCLOAK_SERVER_URL}/admin/realms/{NEST_REALM_NAME}/clients/{client_id}/roles"
    roles_response = requests.get(roles_url, headers=headers)
    roles_response.raise_for_status()
    roles = roles_response.json()

    role_id = None
    for role in roles:
        if role["name"] == client_role_name:
            role_id = role["id"]
            break

    if not role_id:
        raise ValueError(f"Role '{client_role_name}' not found in client '{CLIENT_ID}'")

    # Assign role to user
    assign_url = f"{KEYCLOAK_SERVER_URL}/admin/realms/{NEST_REALM_NAME}/users/{user_id}/role-mappings/clients/{client_id}"
    role_data = [{"id": role_id, "name": client_role_name}]
    response = requests.post(assign_url, headers=headers, data=json.dumps(role_data))
    response.raise_for_status()
    print(f"Assigned role '{client_role_name}' to user {user_id}.")

# Main logic
if __name__ == "__main__":
    try:
        # Step 1: Get the admin token
        token = get_admin_token()
        print("Admin token retrieved.")

        # Step 2: Set the client secret
        # client_secret_value = "k2NKsXJ9pwuSyBMqKzWWLcYlJaZ7q1qb"  # dynamically set or fetch this value
        # set_client_secret(token, client_secret_value)
        # print(f"Client secret set for {CLIENT_ID}.")

        # Step 3: Create or reset users with firstName, lastName, and email
        admin_id = create_or_reset_user(token, "admin", "p", "admin@acme.com", "Admin", "Nest")
        user_id = create_or_reset_user(token, "user", "p", "user@acme.co", "User", "Client")
        print("User passwords created/reset and additional details set.")

        # Step 4: Assign roles to users
        assign_client_role_to_user(token, admin_id, ADMIN_ROLE)
        assign_client_role_to_user(token, user_id, USER_ROLE)
        print(f"Roles assigned: {ADMIN_ROLE} to admin, {USER_ROLE} to user.")

    except Exception as e:
        print(f"An error occurred: {e}")
