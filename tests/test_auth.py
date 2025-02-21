import pytest
from fastapi import status


@pytest.mark.auth
def test_signup(test_client):
    response = test_client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "role": "member",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "test@example.com"


@pytest.mark.auth
@pytest.mark.parametrize(
    "email, password, expected_status",
    [
        ("test@example.com", "testpassword", status.HTTP_200_OK),
        ("wrong@example.com", "testpassword", status.HTTP_401_UNAUTHORIZED),
        ("test@example.com", "wrongpassword", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_login(test_client, email, password, expected_status):
    """Ensure user exists before login test."""

    test_client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "role": "member",
        },
    )

    response = test_client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    print(f"Login Response [{email}]:", response.json())

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert "access_token" in response.json()


@pytest.mark.auth
def test_refresh_token(test_client):
    """Ensure token is retrieved before testing refresh token."""

    # Create user
    test_client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "role": "member",
        },
    )

    # Login to get the token
    login_response = test_client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    print("Login Response:", login_response.json())

    assert (
        login_response.status_code == status.HTTP_200_OK
    ), f"Login failed: {login_response.json()}"

    token = login_response.json().get("access_token")
    assert token, "Token not found in login response"

    # Refresh token request
    refresh_response = test_client.post(
        "/auth/refresh", headers={"Authorization": f"Bearer {token}"}
    )

    print("Refresh Token Response:", refresh_response.json())

    assert (
        refresh_response.status_code == status.HTTP_200_OK
    ), f"Refresh failed: {refresh_response.json()}"
    assert "access_token" in refresh_response.json()


@pytest.mark.auth
@pytest.mark.parametrize(
    "username, email, password, role, expected_status",
    [
        (
            "",
            "valid@example.com",
            "password",
            "member",
            status.HTTP_400_BAD_REQUEST,
        ),  # Empty username
        (
            "validuser",
            "invalid-email",
            "password",
            "member",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),  # Invalid email format
        (
            "validuser",
            "valid@example.com",
            "",
            "member",
            status.HTTP_400_BAD_REQUEST,
        ),  # Empty password
        (
            "validuser",
            "valid@example.com",
            "password",
            "invalid_role",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),  # Invalid role
    ],
)
def test_signup_invalid_inputs(
    test_client, username, email, password, role, expected_status
):
    response = test_client.post(
        "/auth/signup",
        json={"username": username, "email": email, "password": password, "role": role},
    )
    assert response.status_code == expected_status


@pytest.mark.auth
def test_signup_duplicate_email(test_client):
    """Test that duplicate email registration is rejected."""

    first_response = test_client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "duplicate@example.com",
            "password": "password123",
            "role": "member",
        },
    )

    print("First Signup Response:", first_response.json())
    assert (
        first_response.status_code == status.HTTP_200_OK
    ), f"First signup failed: {first_response.json()}"

    duplicate_response = test_client.post(
        "/auth/signup",
        json={
            "username": "newuser",
            "email": "duplicate@example.com",
            "password": "password123",
            "role": "member",
        },
    )

    print("Duplicate Signup Response:", duplicate_response.json())

    assert (
        duplicate_response.status_code == status.HTTP_400_BAD_REQUEST
    ), f"Unexpected response: {duplicate_response.json()}"
    assert duplicate_response.json()["detail"] == "Email already registered"
