import pytest
from fastapi import status


@pytest.fixture
def admin_token(test_client):
    """Fixture to create an admin user and return a valid JWT token."""
    test_client.post(
        "/auth/signup",
        json={
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "adminpass",
            "role": "admin",
        },
    )

    login_response = test_client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "adminpass"},
    )

    assert login_response.status_code == status.HTTP_200_OK
    return login_response.json()["access_token"]


def test_add_book(test_client, admin_token):
    """Test adding a book as an admin."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = test_client.post(
        "/admin/books",
        json={
            "title": "Test Book",
            "author": "Author",
            "available": True,
            "isbn": "9876543210987",
        },
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Test Book"


@pytest.mark.admin
def test_update_book(test_client, admin_token):
    response = test_client.put(
        "/admin/books/1",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Updated Title",
            "author": "Updated Author",
            "isbn": "9876543210987",
        },
    )
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.admin
def test_delete_book(test_client, admin_token):
    response = test_client.delete(
        "/admin/books/1",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.admin
@pytest.mark.parametrize(
    "title, author, isbn, expected_status",
    [
        ("", "Test Author", "1234567890123", status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("Test Book", "", "1234567890123", status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("Test Book", "Test Author", "", status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("Test Book", "Test Author", "invalid_isbn", status.HTTP_400_BAD_REQUEST),
    ],
)
def test_add_book_invalid_inputs(
    test_client, admin_token, title, author, isbn, expected_status
):
    response = test_client.post(
        "/admin/books",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": title, "author": author, "isbn": isbn},
    )
    assert response.status_code == expected_status


@pytest.mark.admin
def test_add_duplicate_isbn(test_client, admin_token):
    test_client.post(
        "/admin/books",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Original Book", "author": "Author", "isbn": "9876543210987"},
    )

    response = test_client.post(
        "/admin/books",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Duplicate Book",
            "author": "Another Author",
            "isbn": "9876543210987",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
