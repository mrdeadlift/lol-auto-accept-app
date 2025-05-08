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
    mock.auto_stop_var = MagicMock()
    mock.auto_stop_var.get = MagicMock(return_value=False)
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
    assert controller.gui.update_ui_on_start.called
    assert controller.tray_icon.update_menu_state.call_args[0][0] is True


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
    assert controller.tray_icon.update_menu_state.called
    assert controller.tray_icon.update_menu_state.call_args[0][0] is True


def test_stop_when_monitoring(controller, mock_thread):
    """stopメソッドのテスト - 監視中の状態からの停止"""
    # 監視中の状態をセットアップ
    controller.monitoring = True
    controller.monitor_thread = mock_thread
    
    # stopメソッドを実行
    controller.stop()
    
    # 状態が変更されたことを確認
    assert controller.monitoring is False
    
    # スレッドのjoinが呼ばれたことを確認
    assert mock_thread.join.called
    
    # 関連コンポーネントのメソッドが呼ばれたことを確認
    assert controller.gui.update_ui_on_stop.called
    assert controller.tray_icon.update_menu_state.call_args[0][0] is False


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
    
    # 状態が変更されたことを確認
    assert controller.monitoring is False
    
    # tray_iconのメソッドが呼ばれたことを確認
    assert controller.tray_icon.update_menu_state.called
    assert controller.tray_icon.update_menu_state.call_args[0][0] is False


def test_show_window_with_gui(controller):
    """show_windowメソッドのテスト - GUIあり"""
    controller.show_window()
    assert controller.gui.show.called


def test_show_window_no_gui(mock_auto_accept):
    """show_windowメソッドのテスト - GUIなし"""
    controller = Controller(mock_auto_accept)
    # GUIがない場合は何も起こらないことを確認
    controller.show_window()  # エラーが発生しないことを確認


def test_exit_with_everything(controller, mock_thread):
    """exitメソッドのテスト - すべてのコンポーネントあり、監視中"""
    # 監視中の状態をセットアップ
    controller.monitoring = True
    controller.monitor_thread = mock_thread
    
    # exitメソッドを実行
    controller.exit()
    
    # 状態が変更されたことを確認
    assert controller.monitoring is False
    assert controller.running is False
    
    # スレッドのjoinが呼ばれたことを確認
    assert mock_thread.join.called
    
    # 関連コンポーネントのメソッドが呼ばれたことを確認
    assert controller.tray_icon.shutdown.called
    assert controller.gui.quit.called


def test_exit_no_gui_no_monitoring(mock_auto_accept, mock_tray_icon):
    """exitメソッドのテスト - GUIなし、監視していない"""
    # GUIなしのControllerを作成
    controller = Controller(mock_auto_accept)
    controller.tray_icon = mock_tray_icon
    
    # exitメソッドを実行
    controller.exit()
    
    # 状態が変更されたことを確認
    assert controller.running is False
    
    # tray_iconのメソッドが呼ばれたことを確認
    assert controller.tray_icon.shutdown.called


def test_monitor_function(controller, mock_thread, mocker):
    """monitor関数のテスト (startメソッド内の内部関数)"""
    # 必要なモックを設定
    mocker.patch('time.sleep')  # sleepをモック
    
    # auto_accept.scan_screenの振る舞いを設定
    # 1回目はボタンが見つからない、2回目は見つかる、その後は監視停止
    scan_results = [False, True]
    controller.auto_accept.scan_screen.side_effect = lambda: scan_results.pop(0) if scan_results else False
    
    # GUIのauto_stop_varをTrueに設定
    controller.gui.auto_stop_var.get.return_value = True
    
    # startメソッドを実行して内部のmonitor関数を呼び出す
    controller.start()
    
    # 監視が開始されたことを確認
    assert controller.monitoring is True
