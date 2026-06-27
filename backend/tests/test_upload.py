import pytest
from fastapi import UploadFile
from app.utils.validators import validate_file

def test_validate_file_too_large():
    class MockFile:
        size = 25 * 1024 * 1024
        filename = "test.pdf"
    with pytest.raises(ValueError) as excinfo:
        validate_file(MockFile())
    assert "exceeds" in str(excinfo.value)

def test_validate_file_invalid_extension():
    class MockFile:
        size = 1024
        filename = "test.txt"
    with pytest.raises(ValueError) as excinfo:
        validate_file(MockFile())
    assert "format" in str(excinfo.value)