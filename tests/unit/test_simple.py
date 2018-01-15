def test_index(webtest):
    """Assert that the application is capable of returning 200.
    """
    resp = webtest.get('/')

    assert resp.status_code == 200
    assert resp.content_type == 'text/html'


def test_not_found(webtest):
    """Assert that the application is capable of returning 400.
    """
    resp = webtest.get('/asdasdasd/', status=404)

    assert resp.status_code == 404
