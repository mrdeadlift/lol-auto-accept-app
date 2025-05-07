import pytest
import sys
import os
import json
from pathlib import Path
from unittest.mock import MagicMock
import tkinter as tk
import threading

# プロジェクトルートをPYTHONPATHに追加
def pytest_configure():
    project_root = str(Path(__file__).parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# デフォルトのテスト用設定
@pytest.fixture
def default_config():
    return {
        "images": {
            "accept_button": "accept_button.png",
            "matching_screen": "matching.png"
        },
        "template_matching": {
            "confidence": 0.7,
            "interval_sec": 0.1  # テスト用に高速化
        }
    }

# テスト用の一時的な画像ファイルを作成
@pytest.fixture
def mock_button_image(tmp_path):
    image_path = tmp_path / "accept_button.png"
    image_path.write_bytes(b"dummy image content")
    return str(image_path)

@pytest.fixture
def mock_matching_image(tmp_path):
    image_path = tmp_path / "matching.png"
    image_path.write_bytes(b"dummy matching image content")
    return str(image_path)

# 設定ファイルをモック
@pytest.fixture
def mock_config_file(tmp_path, default_config):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(default_config), encoding="utf-8")
    return str(config_file)

# tkinterのモック
@pytest.fixture
def mock_tk(mocker):
    # Tkと関連クラスをモック
    mocker.patch("tkinter.Tk")
    mocker.patch("tkinter.Frame")
    mocker.patch("tkinter.Label")
    mocker.patch("tkinter.Button")
    mocker.patch("tkinter.Checkbutton")
    
    # BooleanVarをモック
    bool_var_mock = MagicMock()
    bool_var_mock.get.return_value = False
    mocker.patch("tkinter.BooleanVar", return_value=bool_var_mock)
    
    # イメージ関連をモック
    mocker.patch("PIL.Image.open")
    mocker.patch("PIL.ImageTk.PhotoImage")
    
    return {
        "tk": mocker.patch("tkinter.Tk"),
        "frame": mocker.patch("tkinter.Frame"),
        "label": mocker.patch("tkinter.Label"),
        "button": mocker.patch("tkinter.Button"),
        "checkbutton": mocker.patch("tkinter.Checkbutton"),
        "bool_var": bool_var_mock
    }

# pyautoguiのモック
@pytest.fixture
def mock_pyautogui(mocker):
    locate_mock = mocker.patch("pyautogui.locateOnScreen")
    center_mock = mocker.patch("pyautogui.center")
    click_mock = mocker.patch("pyautogui.click")
    
    return {
        "locate": locate_mock,
        "center": center_mock,
        "click": click_mock
    }

# スレッドのモック
@pytest.fixture
def mock_thread(mocker):
    # 実際にスレッドを作らないようにモックを設定
    thread_mock = MagicMock(spec=threading.Thread)
    thread_mock.start = MagicMock()
    thread_mock.join = MagicMock()
    thread_mock.is_alive = MagicMock(return_value=True)
    
    mocker.patch("threading.Thread", return_value=thread_mock)
    
    # time.sleepもモック化して高速化
    mocker.patch("time.sleep")
    
    return thread_mock

# pystrayのモック
@pytest.fixture
def mock_pystray(mocker):
    icon_mock = MagicMock()
    icon_mock.run = MagicMock()
    icon_mock.stop = MagicMock()
    
    menu_mock = MagicMock()
    menu_item_mock = MagicMock()
    
    mocker.patch("pystray.Icon", return_value=icon_mock)
    mocker.patch("pystray.Menu", return_value=menu_mock)
    mocker.patch("pystray.MenuItem", return_value=menu_item_mock)
    
    return {
        "icon": icon_mock,
        "menu": menu_mock,
        "menu_item": menu_item_mock
    }
