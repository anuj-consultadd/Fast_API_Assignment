import pytest
from fastapi import status


@pytest.fixture
def member_token(test_client):
    """Fixture to create a member user and return a valid JWT token."""
    test_client.post(
        "/auth/signup",
        json={
            "username": "memberuser",
            "email": "member@example.com",
            "password": "memberpass",
            "role": "member",
        },
    )

    login_response = test_client.post(
        "/auth/login",
        data={"username": "member@example.com", "password": "memberpass"},
    )

    assert login_response.status_code == status.HTTP_200_OK, login_response.json()
    return login_response.json()["access_token"]


@pytest.fixture
def create_test_book(test_client, admin_token):
    """Fixture to create a test book before borrowing."""
    response = test_client.post(
        "/admin/books",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Test Book",
            "author": "Author",
            "isbn": "1234567891234",
            "available": True,
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    return response.json()["id"]


import pytest
from fastapi import status


@pytest.mark.user
def test_browse_books(test_client, member_token, create_test_book):
    """Test browsing available books."""
    response = test_client.get(
        "/books/", headers={"Authorization": f"Bearer {member_token}"}
    )

    print("Browse Books Response:", response.json())

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert any(
        book["id"] == create_test_book for book in response.json()
    ), "Test book not found in browse results"


@pytest.mark.user
def test_borrow_book(test_client, member_token, create_test_book):
    """Test borrowing a book."""
    book_id = create_test_book

    response = test_client.post(
        f"/books/{book_id}/borrow", headers={"Authorization": f"Bearer {member_token}"}
    )

    print("Borrow Response:", response.json())

    assert (
        response.status_code == status.HTTP_200_OK
    ), f"Unexpected response: {response.json()}"
    assert response.json()["book_id"] == book_id, "Borrowed book ID mismatch"


@pytest.mark.user
def test_return_book(test_client, member_token, create_test_book):
    """Test returning a borrowed book."""
    book_id = create_test_book

    # First, borrow the book
    borrow_response = test_client.post(
        f"/books/{book_id}/borrow", headers={"Authorization": f"Bearer {member_token}"}
    )
    assert (
        borrow_response.status_code == status.HTTP_200_OK
    ), f"Borrow failed: {borrow_response.json()}"

    # Now return the book
    return_response = test_client.post(
        f"/books/{book_id}/return", headers={"Authorization": f"Bearer {member_token}"}
    )

    print("Return Response:", return_response.json())

    assert (
        return_response.status_code == status.HTTP_200_OK
    ), f"Unexpected response: {return_response.json()}"
    assert return_response.json()["message"] == "Book returned successfully"


@pytest.mark.user
def test_borrow_nonexistent_book(test_client, member_token):
    """Test borrowing a non-existent book (ID 999)."""
    response = test_client.post(
        "/books/999/borrow", headers={"Authorization": f"Bearer {member_token}"}
    )

    print("Borrow Nonexistent Book Response:", response.json())

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Book not found"


@pytest.mark.user
def test_return_unborrowed_book(test_client, member_token, create_test_book):
    """Test returning a book that was never borrowed."""
    book_id = create_test_book

    response = test_client.post(
        f"/books/{book_id}/return", headers={"Authorization": f"Bearer {member_token}"}
    )

    print("Return Unborrowed Book Response:", response.json())

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "No active borrow record found for this book"


@pytest.mark.user
def test_borrow_unavailable_book(test_client, member_token, create_test_book):
    """Test borrowing a book twice (second attempt should fail)."""
    book_id = create_test_book

    response1 = test_client.post(
        f"/books/{book_id}/borrow", headers={"Authorization": f"Bearer {member_token}"}
    )
    assert (
        response1.status_code == status.HTTP_200_OK
    ), f"First borrow failed: {response1.json()}"

    response2 = test_client.post(
        f"/books/{book_id}/borrow", headers={"Authorization": f"Bearer {member_token}"}
    )

    print("Second Borrow Attempt Response:", response2.json())

    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert response2.json()["detail"] == "Book is not available"


@pytest.mark.user
def test_return_nonexistent_book(test_client, member_token):
    """Test returning a non-existent book (ID 999)."""
    response = test_client.post(
        "/books/999/return", headers={"Authorization": f"Bearer {member_token}"}
    )

    print("Return Nonexistent Book Response:", response.json())

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Book not found"
