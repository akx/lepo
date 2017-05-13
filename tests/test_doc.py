def test_docs(client):
    assert '/api/swagger.json' in client.get('/api/docs/').content.decode('utf-8')
    assert client.get('/api/swagger.json').content.startswith(b'{')
