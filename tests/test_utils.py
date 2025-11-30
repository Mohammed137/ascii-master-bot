from app.utilities import check_rate_limit, record_request, init_db
import os, tempfile

def test_rate_limit_tmp_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    # use file based db
    init_db(path)
    ok = check_rate_limit(path, 123, "text", limit=1)
    assert ok is True
    record_request(path, 123, "text")
    ok2 = check_rate_limit(path, 123, "text", limit=1)
    assert ok2 is False
    os.remove(path)
