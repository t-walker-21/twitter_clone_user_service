from unittest.mock import patch
from src.app import get_user_by_id, create_user, update_user, delete_user


@patch('src.app.db')
def test_get_user_by_id(mock_db):
    # Mock the database call
    mock_db.get_user.return_value = {'id': 1, 'name': 'John Doe'}
    
    # Call the function
    user = get_user_by_id(1)
    
    # Assertions
    mock_db.get_user.assert_called_once_with(1)
    assert user == {'id': 1, 'name': 'John Doe'}


@patch('app.db')
def test_create_user(mock_db):
    # Mock the database call
    mock_db.create_user.return_value = {'id': 2, 'name': 'Jane Doe'}
    
    # Call the function
    user = create_user({'name': 'Jane Doe'})
    
    # Assertions
    mock_db.create_user.assert_called_once_with({'name': 'Jane Doe'})
    assert user == {'id': 2, 'name': 'Jane Doe'}


@patch('app.db')
def test_update_user(mock_db):
    # Mock the database call
    mock_db.update_user.return_value = {'id': 1, 'name': 'John Smith'}
    
    # Call the function
    user = update_user(1, {'name': 'John Smith'})
    
    # Assertions
    mock_db.update_user.assert_called_once_with(1, {'name': 'John Smith'})
    assert user == {'id': 1, 'name': 'John Smith'}


@patch('app.db')
def test_delete_user(mock_db):
    # Mock the database call
    mock_db.delete_user.return_value = True
    
    # Call the function
    result = delete_user(1)
    
    # Assertions
    mock_db.delete_user.assert_called_once_with(1)
    assert result is True