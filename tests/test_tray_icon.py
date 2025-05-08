import pytest
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pystray
from PIL import Image
import logging

from src.tray_icon import TrayIcon


@pytest.fixture
def mock_controller():
    """Controllerのモック"""
    controller = MagicMock()
    controller.monitoring = False
    controller.start = MagicMock()
    controller.stop = MagicMock()
    controller.exit = MagicMock()
    controller.show_window = MagicMock()
    return controller


@pytest.fixture
def tray_icon_instance(mock_controller, mock_pystray, mocker):
    """TrayIconインスタンスの作成"""
    # パス関連のモック
    mocker.patch('pathlib.Path.resolve', return_value=Path('/mock/path'))
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.path.join', return_value='/mock/path/resources/tray_icon.png')
    
    # Pillow Image.openのモック
    image_mock = MagicMock(spec=Image.Image)
    mocker.patch('PIL.Image.open', return_value=image_mock)
    
    # スレッドとログのモック
    thread_mock = MagicMock()
    thread_mock.start = MagicMock()
    mocker.patch('threading.Thread', return_value=thread_mock)
    mocker.patch('logging.info')
    mocker.patch('logging.error')
    mocker.patch('logging.warning')
    
    # PyStray Menu 関連のモック
    menu_mock = MagicMock()
    mocker.patch('pystray.Menu', return_value=menu_mock)
    
    # TrayIcon インスタンスを作成
    tray_icon = TrayIcon(mock_controller)
    tray_icon.tray_thread = thread_mock
    
    return tray_icon


def test_init_with_default_icon(mock_controller, mock_pystray, mocker):
    """デフォルトアイコンでの初期化テスト"""
    # パス関連のモック
    mocker.patch('pathlib.Path.resolve', return_value=Path('/mock/path'))
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.path.join', return_value='/mock/path/resources/tray_icon.png')
    
    # Imageモック
    image_mock = MagicMock(spec=Image.Image)
    mocker.patch('PIL.Image.open', return_value=image_mock)
    
    # ログのモック
    log_info_mock = mocker.patch('logging.info')
    
    # TrayIconを作成
    tray_icon = TrayIcon(mock_controller)
    
    # 確認
    assert tray_icon.controller == mock_controller
    assert tray_icon.is_monitoring == mock_controller.monitoring
    assert hasattr(tray_icon, 'icon')
    assert log_info_mock.called


def test_init_with_custom_icon(mock_controller, mock_pystray, mocker):
    """カスタムアイコンでの初期化テスト"""
    # Imageモック
    image_mock = MagicMock(spec=Image.Image)
    mocker.patch('PIL.Image.open', return_value=image_mock)
    
    # 自作アイコンパス
    custom_icon_path = '/custom/icon/path.png'
    
    # TrayIconをカスタムアイコンで作成
    tray_icon = TrayIcon(mock_controller, icon_path=custom_icon_path)
    
    # 確認
    assert mock_pystray['icon'].called
    image_open_calls = mocker.patch('PIL.Image.open').call_args_list
    assert len(image_open_calls) > 0
    assert image_open_calls[0][0][0] == custom_icon_path


def test_init_no_icon_found(mock_controller, mock_pystray, mocker):
    """アイコンが見つからない場合の初期化テスト"""
    # 最初のパスが存在しないが、resources内に1つはPNGがある状況をモック
    mocker.patch('pathlib.Path.resolve', return_value=Path('/mock/path'))
    
    def path_exists_side_effect(path):
        if path == '/mock/path/resources/tray_icon.png':
            return False
        else:
            return True
    
    mocker.patch('os.path.exists', side_effect=path_exists_side_effect)
    mocker.patch('os.path.join', side_effect=lambda *args: '/'.join(args))
    
    # resourcesディレクトリ内のファイルをモック
    def listdir_side_effect(path):
        if path == '/mock/path/resources':
            return ['alternative.png']
        return []
    
    mocker.patch('os.listdir', side_effect=listdir_side_effect)
    
    # Imageモック
    image_mock = MagicMock(spec=Image.Image)
    mocker.patch('PIL.Image.open', return_value=image_mock)
    
    # ログのモック
    log_warning_mock = mocker.patch('logging.warning')
    log_info_mock = mocker.patch('logging.info')
    
    # TrayIconを作成
    tray_icon = TrayIcon(mock_controller)
    
    # 確認
    assert log_warning_mock.called
    assert log_info_mock.called
    assert hasattr(tray_icon, 'icon')


def test_create_menu(tray_icon_instance, mock_pystray):
    """メニュー作成のテスト"""
    # _create_menu を呼び出す
    menu = tray_icon_instance._create_menu()
    
    # PyStray.Menu が呼ばれたことを確認
    assert mock_pystray['menu'] == menu
    assert mock_pystray['menu_item'].call_count >= 4  # 4つ以上のメニューアイテム


def test_handle_open(tray_icon_instance, mock_controller):
    """_handle_openメソッドのテスト"""
    # _handle_open を呼び出す
    tray_icon_instance._handle_open()
    
    # controllerのshow_windowが呼ばれたことを確認
    assert mock_controller.show_window.called


def test_handle_start(tray_icon_instance, mock_controller):
    """_handle_startメソッドのテスト"""
    # _handle_start を呼び出す
    tray_icon_instance._handle_start()
    
    # controllerのstartが呼ばれたことを確認
    assert mock_controller.start.called


def test_handle_stop(tray_icon_instance, mock_controller):
    """_handle_stopメソッドのテスト"""
    # _handle_stop を呼び出す
    tray_icon_instance._handle_stop()
    
    # controllerのstopが呼ばれたことを確認
    assert mock_controller.stop.called


def test_handle_exit(tray_icon_instance, mock_controller):
    """_handle_exitメソッドのテスト"""
    # _handle_exit を呼び出す
    tray_icon_instance._handle_exit()
    
    # shutdown が呼ばれたことを確認
    assert mock_controller.exit.called


def test_update_menu_state(tray_icon_instance, mocker):
    """update_menu_stateメソッドのテスト"""
    # 必要なモック
    log_info_mock = mocker.patch('logging.info')
    
    # 初期状態を確認
    assert tray_icon_instance.is_monitoring is False
    
    # update_menu_state を呼び出す
    tray_icon_instance.update_menu_state(True)
    
    # 状態が更新されたことを確認
    assert tray_icon_instance.is_monitoring is True
    assert log_info_mock.called


def test_run(tray_icon_instance):
    """runメソッドのテスト"""
    # runメソッドを呼び出す
    tray_icon_instance.run()
    
    # スレッドが開始されたことを確認
    assert tray_icon_instance.tray_thread.start.called


def test_shutdown(tray_icon_instance, mock_pystray):
    """shutdownメソッドのテスト"""
    # shutdownメソッドを呼び出す
    tray_icon_instance.shutdown()
    
    # iconのstopメソッドが呼ばれたことを確認
    assert mock_pystray['icon'].stop.called


def test_shutdown_exception(tray_icon_instance, mock_pystray, mocker):
    """shutdownメソッドの例外テスト"""
    # stopメソッドが例外を投げるように設定
    mock_pystray['icon'].stop.side_effect = Exception("Stop error")
    
    # ログのモック
    log_error_mock = mocker.patch('logging.error')
    
    # shutdownメソッドを呼び出す
    tray_icon_instance.shutdown()
    
    # エラーログが記録されたことを確認
    assert log_error_mock.called
