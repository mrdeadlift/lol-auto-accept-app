import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image

# Import the module directly instead of executing the script
sys.path.insert(0, str(Path(__file__).parent.parent))
from src import convert_to_ico


@pytest.fixture
def mock_image():
    """PIL Imageのモック"""
    image_mock = MagicMock(spec=Image.Image)
    image_mock.save = MagicMock()
    return image_mock


def test_convert_png_to_ico(mock_image, tmp_path, mocker):
    """PNG→ICO変換の正常系テスト"""
    # テスト用の一時的なファイルパスを作成
    png_path = tmp_path / "tray_icon.png"
    ico_path = tmp_path / "tray_icon.ico"
    
    # 各種モックの設定
    mocker.patch('pathlib.Path.__new__', return_value=Path(tmp_path))
    mocker.patch('pathlib.Path.resolve', return_value=Path(tmp_path))
    mocker.patch('os.path.join', side_effect=lambda *args: str(Path(*args)))
    mocker.patch('PIL.Image.open', return_value=mock_image)
    print_mock = mocker.patch('builtins.print')
    
    # テスト用のファイルを作成
    png_path.touch()
    
    # 直接関数を呼び出す
    with patch.object(convert_to_ico, '__file__', str(tmp_path / "convert_to_ico.py")):
        convert_to_ico.convert_png_to_ico()
    
    # 検証
    assert mock_image.save.called
    assert 'format' in mock_image.save.call_args[1]
    assert mock_image.save.call_args[1]['format'] == 'ICO'
    assert print_mock.called


def test_convert_png_to_ico_file_not_found(mocker):
    """入力ファイルが存在しない場合のテスト"""
    # 存在しないファイルパスを設定
    non_existent_path = "/path/to/nonexistent/tray_icon.png"
    
    # 各種モックの設定
    mocker.patch('pathlib.Path.resolve', return_value=Path("/path/to/nonexistent"))
    mocker.patch('os.path.join', return_value=non_existent_path)
    mocker.patch('PIL.Image.open', side_effect=FileNotFoundError("File not found"))
    
    # 直接関数を呼び出して例外が発生することを確認
    with pytest.raises(FileNotFoundError):
        with patch.object(convert_to_ico, '__file__', "/path/to/nonexistent/convert_to_ico.py"):
            convert_to_ico.convert_png_to_ico()


def test_convert_png_to_ico_save_error(mock_image, tmp_path, mocker):
    """保存時にエラーが発生する場合のテスト"""
    # テスト用の一時的なファイルパスを作成
    png_path = tmp_path / "tray_icon.png"
    
    # 各種モックの設定
    mocker.patch('pathlib.Path.__new__', return_value=Path(tmp_path))
    mocker.patch('pathlib.Path.resolve', return_value=Path(tmp_path))
    mocker.patch('os.path.join', side_effect=lambda *args: str(Path(*args)))
    mocker.patch('PIL.Image.open', return_value=mock_image)
    
    # 保存時にエラーを発生させる
    mock_image.save.side_effect = PermissionError("Permission denied")
    
    # テスト用のファイルを作成
    png_path.touch()
    
    # 直接関数を呼び出して例外が発生することを確認
    with pytest.raises(PermissionError):
        with patch.object(convert_to_ico, '__file__', str(tmp_path / "convert_to_ico.py")):
            convert_to_ico.convert_png_to_ico()
