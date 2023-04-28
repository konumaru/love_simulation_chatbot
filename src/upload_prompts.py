import os
import pathlib

from utils.storage import GCSFileManager


def main() -> None:
    # Upload charactor settings.
    gcs = GCSFileManager(os.environ["GCS_BUCKET_NAME"])
    charactor_dir = pathlib.Path("data/prompts/charactor")
    for filepath in charactor_dir.glob("*.json"):
        gcs.create_file(filepath, f"prompts/charactor/{filepath.name}")

    # Upload conversation prompt.
    gcs.create_file(
        "data/prompts/start_conversation_v2.txt",
        "prompts/start_conversation_v2.txt",
    )


if __name__ == "__main__":
    main()
