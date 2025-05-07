import pytest
from unittest.mock import MagicMock, patch
import threading
import time
import logging

from src.controller import Controller


@pytest.fixture
def mock_auto_accept():
    """LoLAutoAcceptのモック"""
    mock = MagicMock()
    mock.scan_screen = MagicMock(return_value=False)
    mock.run = MagicMock()
    return mock


@pytest.fixture
def mock_gui():
    """GUIのモック"""
    mock = MagicMock()
    mock.update_ui_on_start = MagicMock()
    mock.update_ui_on_stop = MagicMock()
    mock.show = MagicMock()
    mock.quit = MagicMock()
    return mock


@pytest.fixture
def mock_tray_icon():
    """TrayIconのモック"""
    mock = MagicMock()
    mock.update_menu_state = MagicMock()
    mock.shutdown = MagicMock()
    return mock


@pytest.fixture
def controller(mock_auto_accept, mock_gui, mock_tray_icon):
    """Controllerインスタンスの作成"""
    controller = Controller(mock_auto_accept, mock_gui)
    controller.tray_icon = mock_tray_icon
    return controller


def test_controller_init(mock_auto_accept):
    """Controllerの初期化テスト"""
    # GUIありのケース
    gui_mock = MagicMock()
    controller = Controller(mock_auto_accept, gui_mock)
    
    assert controller.auto_accept == mock_auto_accept
    assert controller.gui == gui_mock
    assert controller.running is True
    assert controller.monitoring is False
    assert controller.monitor_thread is None
    
    # GUIなしのケース
    controller_no_gui = Controller(mock_auto_accept)
    assert controller_no_gui.auto_accept == mock_auto_accept
    assert controller_no_gui.gui is None
    assert controller_no_gui.running is True
    assert controller_no_gui.monitoring is False
    assert controller_no_gui.monitor_thread is None


def test_start_not_monitoring(controller, mock_thread):
    """startメソッドのテスト - 監視していない状態からの開始"""
    # 監視していない状態を確認
    assert controller.monitoring is False
    assert controller.monitor_thread is None
    
    # startメソッドを実行
    controller.start()
    
    # 状態が変更されたことを確認
    assert controller.monitoring is True
    assert controller.monitor_thread is not None
    
    # 関連コンポーネントのメソッドが呼ばれたことを確認
    controller.gui.update_ui_on_start.assert_called_once()
    controller.tray_icon.update_menu_state.assert_called_once_with(True)


def test_start_already_monitoring(controller, mock_thread):
    """startメソッドのテスト - 既に監視中の状態からの開始"""
    # 監視中の状態をセットアップ
    controller.monitoring = True
    controller.monitor_thread = mock_thread
    
    # startメソッドを実行
    controller.start()
    
    # 何も変更されないことを確認
    assert controller.monitoring is True
    assert controller.monitor_thread == mock_thread
    
    # UI更新メソッドが呼ばれないことを確認
    controller.gui.update_ui_on_start.assert_not_called()
    controller.tray_icon.update_menu_state.assert_not_called()


def test_start_no_gui(mock_auto_accept, mock_tray_icon, mock_thread):
    """GUIなしでのstartメソッドのテスト"""
    # GUIなしのControllerを作成
    controller = Controller(mock_auto_accept)
    controller.tray_icon = mock_tray_icon
    
    # startメソッドを実行
    controller.start()
    
    # 状態が変更されたことを確認
    assert controller.monitoring is True
    assert controller.monitor_thread is not None
    
    # tray_iconのメソッドが呼ばれたことを確認
    controller.tray_icon.update_menu_state.assert_called_once_with(True)


def test_stop_when_monitoring(controller, mock_thread):
    """stopメソッドのテスト - 監視中の状態からの停止"""
    # 監視中の状態をセットアップ
    controller.monitoring = True
    controller.monitor_thread = mock_thread
    
    # stopメソッドを実行
    controller.stop()
    
    # 状態が変更されたことを確認
    assert controller.monitoring is False
    assert controller.monitor_thread is None
    
    # スレッドのjoinが呼ばれたことを確認
    mock_thread.join.assert_called_once()
    
    # 関連コンポーネントのメソッドが呼ばれたことを確認
    controller.gui.update_ui_on_stop.assert_called_once()
    controller.tray_icon.update_menu_state.assert_called_once_with(False)


def test_stop_not_monitoring(controller):
    """stopメソッドのテスト - 監視していない状態からの停止"""
    # 監視していない状態を確認
    assert controller.monitoring is False
    assert controller.monitor_thread is None
    
    # stopメソッドを実行
    controller.stop()
    
    # 何も変更されないことを確認
    assert controller.monitoring is False
    assert controller.monitor_thread is None
    
    # UI更新メソッドが呼ばれないことを確認
    controller.gui.update_ui_on_stop.assert_not_called()
    controller.tray_icon.update_menu_state.assert_not_called()


def test_stop_no_gui(mock_auto_accept, mock_tray_icon, mock_thread):
    """GUIなしでのstopメソッドのテスト"""
    # GUIなしのControllerを作成し、監視中の状態に設定
    controller = Controller(mock_auto_accept)
    controller.tray_icon = mock_tray_icon
    controller.monitoring = True
    controller.monitor_thread = mock_thread
    
    # stopメソッドを実行
    controller.stop()
    
    # u72b6u614bu304cu5909u66f4u3055u308cu305fu3053u3068u3092u78bau8a8d
    assert controller.monitoring is False
    assert controller.monitor_thread is None
    
    # tray_iconu306eu30e1u30bdu30c3u30c9u304cu547cu3070u308cu305fu3053u3068u3092u78bau8a8d
    controller.tray_icon.update_menu_state.assert_called_once_with(False)


def test_show_window_with_gui(controller):
    """show_windowメソッドのテスト - GUIあり"""
    controller.show_window()
    controller.gui.show.assert_called_once()


def test_show_window_no_gui(mock_auto_accept):
    """show_windowメソッドのテスト - GUIなし"""
    controller = Controller(mock_auto_accept)
    # GUIがない場合は何も起こらないことを確認
    controller.show_window()  # エラーが発生しないことを確認


def test_exit_with_everything(controller, mock_thread):
    """exitメソッドのテスト - すべてのコンポーネントあり、監視中"""
    # u76e3u8996u4e2du306eu72b6u614bu3092u30bbu30c3u30c8u30a2u30c3u30d7
    controller.monitoring = True
    controller.monitor_thread = mock_thread
    
    # exitu30e1u30bdu30c3u30c9u3092u5b9fu884c
    controller.exit()
    
    # u72b6u614bu304cu5909u66f4u3055u308cu305fu3053u3068u3092u78bau8a8d
    assert controller.monitoring is False
    assert controller.running is False
    
    # u30b9u30ecu30c3u30c9u306ejoinu304cu547cu3070u308cu305fu3053u3068u3092u78bau8a8d
    mock_thread.join.assert_called_once()
    
    # u95a2u9023u30b3u30f3u30ddu30fcu30cdu30f3u30c8u306eu30e1u30bdu30c3u30c9u304cu547cu3070u308cu305fu3053u3068u3092u78bau8a8d
    controller.tray_icon.shutdown.assert_called_once()
    controller.gui.quit.assert_called_once()


def test_exit_no_gui_no_monitoring(mock_auto_accept, mock_tray_icon):
    """exitu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8 - GUIu306au3057u3001u76e3u8996u3057u3066u3044u306au3044"""
    # GUIu306au3057u306eControlleru3092u4f5cu6210
    controller = Controller(mock_auto_accept)
    controller.tray_icon = mock_tray_icon
    
    # exitu30e1u30bdu30c3u30c9u3092u5b9fu884c
    controller.exit()
    
    # u72b6u614bu304cu5909u66f4u3055u308cu305fu3053u3068u3092u78bau8a8d
    assert controller.running is False
    
    # tray_iconu306eu30e1u30bdu30c3u30c9u304cu547cu3070u308cu305fu3053u3068u3092u78bau8a8d
    controller.tray_icon.shutdown.assert_called_once()


def test_monitoring_thread(controller, mock_thread, mocker):
    """_monitoring_threadu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    # u5fc5u8981u306au30e2u30c3u30afu3092u8a2du5b9a
    mocker.patch('time.sleep')  # sleepu3092u30e2u30c3u30af
    
    # u76e3u8996u30b9u30ecu30c3u30c9u3092u5b9fu884cu3059u308bu305fu3081u306eu72b6u614bu3092u8a2du5b9a
    controller.monitoring = True
    
    # auto_accept.scan_screenu306eu632fu308bu821eu3044u3092u8a2du5b9a
    # 1u56deu76eeu306fu30dcu30bfu30f3u304cu898bu3064u304bu3089u306au3044u30012u56deu76eeu306fu898bu3064u304bu308bu3001u305du306eu5f8cu306fu76e3u8996u505cu6b62
    scan_results = [False, True]
    controller.auto_accept.scan_screen.side_effect = lambda: scan_results.pop(0) if scan_results else False
    
    # _monitoring_threadu30e1u30bdu30c3u30c9u3092u5b9fu884c
    controller._monitoring_thread()
