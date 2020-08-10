def test_announcement_api(announcement, client):
    r = client.get('/api/announcement/')
    assert r.data[0]['content'] == announcement.content

    r = client.get(f'/api/announcement/?challenge={announcement.challenge.id}')
    assert r.data[0]['content'] == announcement.content
