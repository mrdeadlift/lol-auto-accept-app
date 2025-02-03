import pytest
from unittest.mock import MagicMock, patch
import os
import sys
import logging
from src.main import LoLAutoAccept

# 画像が見つからない場合のテスト
def test_init_no_image():
    with pytest.raises(SystemExit) as exc_info:
        with patch('os.path.exists', return_value=False):
            LoLAutoAccept()
    assert exc_info.value.code == 1

# 画像が存在する場合の初期化テスト
def test_init_with_image():
    with patch('os.path.exists', return_value=True):
        auto_accept = LoLAutoAccept()
        assert auto_accept.button_image == 'accept_button.png'

# scan_screen のテスト - ボタンが見つからない場合
def test_scan_screen_button_not_found():
    with patch('os.path.exists', return_value=True):
        auto_accept = LoLAutoAccept()
        with patch('pyautogui.locateOnScreen', return_value=None):
            result = auto_accept.scan_screen()
            assert result == False

# scan_screen のテスト - ボタンが見つかった場合
def test_scan_screen_button_found():
    with patch('os.path.exists', return_value=True):
        auto_accept = LoLAutoAccept()
        mock_pos = MagicMock()
        mock_center = (100, 100)
        
        with patch('pyautogui.locateOnScreen', return_value=mock_pos), \
             patch('pyautogui.center', return_value=mock_center), \
             patch('pyautogui.click') as mock_click, \
             patch('time.sleep'):
            
            result = auto_accept.scan_screen()
            
            assert result == True
            mock_click.assert_called_once_with(mock_center)

# scan_screen のテスト - 例外が発生した場合
def test_scan_screen_exception():
    with patch('os.path.exists', return_value=True):
        auto_accept = LoLAutoAccept()
        with patch('pyautogui.locateOnScreen', side_effect=Exception("Test error")):
            result = auto_accept.scan_screen()
            assert result == False
