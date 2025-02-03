import pytest
import sys
import os
from pathlib import Path

# プロジェクトルートをPYTHONPATHに追加
def pytest_configure():
    project_root = str(Path(__file__).parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# テスト用の一時的な画像ファイルを作成
@pytest.fixture
def mock_button_image(tmp_path):
    image_path = tmp_path / "accept_button.png"
    image_path.write_bytes(b"dummy image content")
    return str(image_path)
