from src.utils.storage import GCSFileManager


def test_create_file():
    gcs = GCSFileManager("linebot-storage")
    gcs.create_file("tests/test_storage.py", "test_storage.py")
    _ = gcs.read_file("test_storage.py")
    filelist = gcs.list_files()
    assert len(filelist) > 0
    gcs.delete_file("test_storage.py")
