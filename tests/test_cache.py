def test_cache_is_used_for_errors(client, transactional_db, caplog):
    client.get('/api/v1/cars/incorrect')
    client.get('/api/v1/cars/incorrect')
    assert (
        'Found response hash in DB. Response already checked and is invalid. Re-logging error from cache.' in caplog.messages
    )


def test_cache_is_used_for_valid_responses(client, transactional_db, caplog):
    client.get('/api/v1/cars/correct')
    client.get('/api/v1/cars/correct')
    assert 'Found response hash in DB. Response already checked and is valid.' in caplog.messages


def test_cache_is_invalidated_when_schema_changes(client, transactional_db, caplog):
    # TODO: figure out a good way of doing this
    pass
