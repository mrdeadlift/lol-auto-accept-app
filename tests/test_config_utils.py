import pytest
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch, mock_open
import sys

from src.config_utils import load_config, save_config, get_config_path, parse_arguments, DEFAULT_CONFIG


def test_get_config_path_normal():
    """通常時のconfig_pathの取得テスト"""
    with patch.object(sys, 'frozen', False, create=True):
        path = get_config_path()
        assert isinstance(path, Path)
        assert path.name == 'config.json'
        assert 'lol-auto-accept-app' in str(path)


def test_get_config_path_frozen():
    """frozen時のconfig_pathの取得テスト"""
    with patch.object(sys, 'frozen', True, create=True), \
         patch.object(sys, '_MEIPASS', 'mock_meipass', create=True):
        path = get_config_path()
        assert isinstance(path, Path)
        assert path.name == 'config.json'
        assert str(path).startswith('mock_meipass')


def test_load_config_success(mock_config_file):
    """設定ファイルの正常読み込みテスト"""
    with patch('src.config_utils.get_config_path', return_value=Path(mock_config_file)):
        config = load_config()
        assert config is not None
        assert 'images' in config
        assert 'template_matching' in config
        assert config['images']['accept_button'] == 'accept_button.png'
        assert config['template_matching']['confidence'] == 0.7


def test_load_config_file_not_exists():
    """設定ファイルが存在しない場合のテスト"""
    with patch('src.config_utils.get_config_path') as mock_path:
        # 存在しないパスを返す
        mock_path.return_value = Path('/not/exists/config.json')
        config = load_config()
        # デフォルト設定が返されることを確認
        assert config == DEFAULT_CONFIG


def test_load_config_invalid_json(tmp_path):
    """無効なJSON形式の設定ファイルを読み込むテスト"""
    # 不正なJSONを作成
    invalid_json = tmp_path / "invalid_config.json"
    invalid_json.write_text("This is not a valid JSON", encoding="utf-8")
    
    with patch('src.config_utils.get_config_path', return_value=invalid_json), \
         patch('src.config_utils.logging.error') as mock_error:
        config = load_config()
        # エラーがログに記録されたことを確認
        assert mock_error.called
        # デフォルト設定が返されることを確認
        assert config == DEFAULT_CONFIG


def test_save_config_success(tmp_path, default_config):
    """設定ファイルの正常保存テスト"""
    config_path = tmp_path / "save_config.json"
    
    with patch('src.config_utils.get_config_path', return_value=config_path):
        # 設定を保存
        save_config(default_config)
        
        # ファイルが作成されていることを確認
        assert config_path.exists()
        
        # 保存された内容を検証
        saved_config = json.loads(config_path.read_text(encoding="utf-8"))
        assert saved_config == default_config


def test_save_config_permission_error(default_config):
    """保存時の権限エラーテスト"""
    with patch('src.config_utils.get_config_path'), \
         patch('pathlib.Path.write_text', side_effect=PermissionError("Permission denied")), \
         patch('src.config_utils.logging.error') as mock_error:
        # save_config doesn't return anything, so we just check if error logging is called
        save_config(default_config)
        assert mock_error.call_count > 0


def test_save_config_io_error(default_config):
    """保存時のIOエラーテスト"""
    with patch('src.config_utils.get_config_path'), \
         patch('pathlib.Path.write_text', side_effect=IOError("IO Error")), \
         patch('src.config_utils.logging.error') as mock_error:
        # save_config doesn't return anything, so we just check if error logging is called
        save_config(default_config)
        assert mock_error.call_count > 0


def test_parse_arguments_default():
    """デフォルトのコマンドライン引数解析テスト"""
    with patch('sys.argv', ['main.py']):
        args = parse_arguments()
        assert args.nogui is False


def test_parse_arguments_nogui():
    """--noguiオプション指定時のテスト"""
    with patch('sys.argv', ['main.py', '--nogui']):
        args = parse_arguments()
        assert args.nogui is True
