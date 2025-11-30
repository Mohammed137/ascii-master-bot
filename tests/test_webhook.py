from app.main import process_update

def test_process_update_no_token():
    # call with minimal update; expecting error because token empty
    res = process_update({"message": {"text": "hi", "chat": {"id": 1}, "from": {"id": 1}}}, bot_token="", db_path=":memory:", admin_id="")
    assert isinstance(res, dict)
