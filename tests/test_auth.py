from auth import authenticate_user   # import your auth function

def test_auth_success():
    assert authenticate_user("omar", "123") == True

def test_auth_fail():
    assert authenticate_user("admin", "wrongpass") == False
