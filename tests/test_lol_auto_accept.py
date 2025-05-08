import pytest
import os
import sys
import time
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

try:
    import pyautogui
except ImportError:
    pyautogui = MagicMock()
    pyautogui.ImageNotFoundException = Exception

from src.lol_auto_accept import LoLAutoAccept


@pytest.fixture
def lol_auto_accept_instance(default_config, mocker, tmp_path):
    base_dir = str(tmp_path)
    
    # Path.resolveとPath.parentなどを適切にモック
    mock_path = MagicMock(spec=Path)
    mock_path.resolve.return_value = mock_path
    mock_path.parent.parent = base_dir
    mocker.patch('pathlib.Path.__new__', return_value=mock_path)
    
    # os.path.exists でパスが存在すると判定されるようモック
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.path.join', return_value=f"{base_dir}/resources/accept_button.png")
    mocker.patch('os.path.dirname', return_value=f"{base_dir}/resources")
    
    # 例外防止用にログ出力をモック
    mocker.patch('logging.info')
    mocker.patch('logging.error')
    
    # sys._MEIPASSも必要ならモック
    # mocker.patch.object(sys, '_MEIPASS', f"{base_dir}/meipass", create=True)
    
    return LoLAutoAccept(default_config)


def test_init_normal(default_config, mocker, tmp_path):
    """LoLAutoAcceptの初期化正常ケースのテスト"""
    base_dir = str(tmp_path)
    
    # ファイルが存在するケース
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.path.join', return_value=f"{base_dir}/resources/accept_button.png")
    mocker.patch('pathlib.Path.resolve', return_value=Path(base_dir))
    mocker.patch('logging.info')
    
    instance = LoLAutoAccept(default_config)
    
    assert instance.button_image == default_config['images']['accept_button']
    assert instance.confidence == default_config['template_matching']['confidence']
    assert instance.interval_sec == default_config['template_matching']['interval_sec']
    assert instance.button_image_path == f"{base_dir}/resources/accept_button.png"


def test_init_no_image(default_config, mocker, tmp_path):
    """画像が見つからない場合の初期化テスト"""
    base_dir = str(tmp_path)
    
    mocker.patch('os.path.exists', return_value=False)
    mocker.patch('os.path.join', return_value=f"{base_dir}/not_exists/accept_button.png")
    mocker.patch('pathlib.Path.resolve', return_value=Path(base_dir))
    mocker.patch('logging.error')
    
    # 画像が見つからない場合はsys.exit(1)が呼ばれるため
    with pytest.raises(SystemExit) as excinfo:
        instance = LoLAutoAccept(default_config)
    
    assert excinfo.value.code == 1


@pytest.mark.parametrize("button_exists", [True, False])
def test_scan_screen_button_detection(lol_auto_accept_instance, mock_pyautogui, button_exists):
    """scan_screenがボタンを検出するかしないかのテスト"""
    # locateOnScreenの戻り値を設定
    if button_exists:
        mock_pyautogui['locate'].return_value = (100, 100, 50, 50)  # 位置情報を擬似的に返す
        mock_pyautogui['center'].return_value = (125, 125)  # ボタンの中心座標
    else:
        mock_pyautogui['locate'].return_value = None
    
    # scan_screenを実行
    result = lol_auto_accept_instance.scan_screen()
    
    # 結果を検証
    assert result is button_exists
    
    # ボタンが見つかった場合はクリックされるはず
    if button_exists:
        mock_pyautogui['center'].assert_called_once_with((100, 100, 50, 50))
        mock_pyautogui['click'].assert_called_once_with((125, 125))
    else:
        assert not mock_pyautogui['click'].called


def test_scan_screen_image_not_found_exception(lol_auto_accept_instance, mocker):
    """ImageNotFoundExceptionが発生するケースのテスト"""
    # ImageNotFoundExceptionを発生させる
    mocker.patch('pyautogui.locateOnScreen', side_effect=pyautogui.ImageNotFoundException("Image not found"))
    
    # 例外が適切に処理され、Falseが返されることを確認
    result = lol_auto_accept_instance.scan_screen()
    assert result is False


def test_scan_screen_general_exception(lol_auto_accept_instance, mocker):
    """一般的な例外が発生するケースのテスト"""
    # 一般的な例外を発生させる
    mocker.patch('pyautogui.locateOnScreen', side_effect=Exception("General error"))
    mocker.patch('time.time', return_value=1000)  # 現在時刻のモック
    mock_error = mocker.patch('logging.error')
    
    # エラーが処理され、Falseが返されることを確認
    result = lol_auto_accept_instance.scan_screen()
    assert result is False
    assert mock_error.called  # エラーログが出力されている


def test_scan_screen_error_cooldown(lol_auto_accept_instance, mocker):
    """エラーログ出力のクールダウン機能テスト"""
    # エラー発生条件を設定
    mocker.patch('pyautogui.locateOnScreen', side_effect=Exception("Cooldown test error"))
    mock_error = mocker.patch('logging.error')
    
    # 最初のエラー（クールダウンなし）
    mocker.patch('time.time', return_value=1000)
    lol_auto_accept_instance.last_error_time = 0
    result1 = lol_auto_accept_instance.scan_screen()
    assert result1 is False
    assert mock_error.call_count == 1  # エラーログ出力される
    
    # クールダウン期間中のエラー
    mock_error.reset_mock()
    mocker.patch('time.time', return_value=1010)  # 10秒後（クールダウン60秒）
    lol_auto_accept_instance.last_error_time = 1000
    result2 = lol_auto_accept_instance.scan_screen()
    assert result2 is False
    assert not mock_error.called  # クールダウン中なのでエラーログは出力されない
    
    # クールダウン後のエラー
    mock_error.reset_mock()
    mocker.patch('time.time', return_value=1070)  # 70秒後（クールダウン終了）
    lol_auto_accept_instance.last_error_time = 1000
    result3 = lol_auto_accept_instance.scan_screen()
    assert result3 is False
    assert mock_error.call_count == 1  # クールダウン終了後なのでエラーログが出力される


def test_run_normal_exit(lol_auto_accept_instance, mocker):
    """run関数の正常終了（KeyboardInterrupt）テスト"""
    # scan_screenが1回だけ呼ばれた後にKeyboardInterruptを発生させる
    scan_mock = mocker.patch.object(
        lol_auto_accept_instance, 'scan_screen',
        side_effect=[False, KeyboardInterrupt()]
    )
    mocker.patch('time.sleep')  # sleep関数をモック
    mock_info = mocker.patch('logging.info')
    
    # run関数を実行
    lol_auto_accept_instance.run()
    
    # 検証
    assert scan_mock.call_count == 2
    assert mock_info.call_count >= 2  # 少なくとも起動と終了のログが出るはず


def test_run_exception_exit(lol_auto_accept_instance, mocker):
    """run関数の例外終了テスト"""
    # scan_screenが1回だけ呼ばれた後に例外を発生させる
    scan_mock = mocker.patch.object(
        lol_auto_accept_instance, 'scan_screen',
        side_effect=[False, Exception("Unexpected error")]
    )
    mocker.patch('time.sleep')  # sleep関数をモック
    mock_info = mocker.patch('logging.info')
    mock_error = mocker.patch('logging.error')
    
    # run関数を実行
    lol_auto_accept_instance.run()
    
    # 検証
    assert scan_mock.call_count == 2
    assert mock_error.called  # エラーログが出力されている
    assert mock_info.call_count >= 1  # 少なくとも1回はinfoログが出るはず
