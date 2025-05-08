import pytest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

try:
    import tkinter as tk
except ImportError:
    tk = MagicMock()

from src.auto_accept_gui import AutoAcceptGUI


@pytest.fixture
def mock_controller():
    """Controllerのモック"""
    controller = MagicMock()
    controller.monitoring = False
    controller.start = MagicMock()
    controller.stop = MagicMock()
    controller.exit = MagicMock()
    
    # auto_acceptプロパティのモック
    controller.auto_accept = MagicMock()
    controller.auto_accept.config = {
        'images': {
            'accept_button': 'accept_button.png',
            'matching_screen': 'matching.png'
        },
        'template_matching': {
            'confidence': 0.7,
            'interval_sec': 0.1
        }
    }
    
    return controller


@pytest.fixture
def gui_instance(mock_controller, mocker):
    """AutoAcceptGUIインスタンスの作成"""
    # 停止状態のボタンをモック
    start_button = MagicMock()
    stop_button = MagicMock()
    status_label = MagicMock()
    exit_button = MagicMock()
    
    # パス関連のモック
    mocker.patch('pathlib.Path.resolve', return_value=Path('/mock/path'))
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.path.join', return_value='/mock/path/resources/tray_icon.ico')
    
    # スレッド関連のモック
    thread_mock = MagicMock()
    thread_mock.start = MagicMock()
    mocker.patch('threading.Thread', return_value=thread_mock)
    
    # timeとログのモック
    mocker.patch('time.sleep')
    mocker.patch('logging.info')
    mocker.patch('logging.error')
    mocker.patch('logging.warning')
    
    # tk.Tkと関連クラスの振る舞いを設定
    root_mock = MagicMock()
    root_mock.title = MagicMock()
    root_mock.geometry = MagicMock()
    root_mock.resizable = MagicMock()
    root_mock.configure = MagicMock()
    root_mock.option_add = MagicMock()
    root_mock.protocol = MagicMock()
    root_mock.iconbitmap = MagicMock()
    root_mock.iconphoto = MagicMock()
    root_mock.withdraw = MagicMock()
    root_mock.deiconify = MagicMock()
    root_mock.lift = MagicMock()
    root_mock.focus_force = MagicMock()
    root_mock.quit = MagicMock()
    root_mock.mainloop = MagicMock()
    root_mock.after = MagicMock()
    root_mock.destroy = MagicMock()
    root_mock.iconify = MagicMock()
    mocker.patch('tkinter.Tk', return_value=root_mock)
    
    # フレームのモック
    frame_mock = MagicMock()
    mocker.patch('tkinter.Frame', return_value=frame_mock)
    
    # ラベルのモック
    mocker.patch('tkinter.Label', return_value=status_label)
    
    # ボタンのモック - 複数回呼ばれるのでリストで返す
    button_mock = MagicMock()
    button_mock.side_effect = [start_button, stop_button, exit_button]
    mocker.patch('tkinter.Button', side_effect=[start_button, stop_button, exit_button])
    
    # チェックボタンのモック
    checkbutton_mock = MagicMock()
    mocker.patch('tkinter.Checkbutton', return_value=checkbutton_mock)
    
    # BooleanVarのモック
    bool_var_mock = MagicMock()
    bool_var_mock.get.return_value = False
    mocker.patch('tkinter.BooleanVar', return_value=bool_var_mock)
    
    # PIL関連のモック
    mocker.patch('PIL.Image.open')
    mocker.patch('PIL.ImageTk.PhotoImage')
    
    # pyautoguiのモック
    mocker.patch('pyautogui.locateOnScreen')
    
    # AutoAcceptGUIインスタンスを作成
    gui = AutoAcceptGUI(mock_controller)
    
    # 必要なプロパティを直接設定
    gui.start_button = start_button
    gui.stop_button = stop_button
    gui.status_label = status_label
    gui.exit_button = exit_button
    gui.root = root_mock
    gui.auto_monitor_thread = thread_mock
    gui.auto_start_var = bool_var_mock
    gui.auto_stop_var = bool_var_mock
    
    return gui


def test_gui_initialization(gui_instance, mock_controller):
    """GUIの初期化テスト"""
    # このテストはレベルの高いものなので、gui_instanceのフィクスチャに依存している
    # テスト用に必要な assertions
    assert gui_instance.controller == mock_controller
    assert gui_instance.root is not None
    
    # rootのprotocolメソッドがWM_DELETE_WINDOWとhideメソッドを登録していることを確認
    assert gui_instance.root.protocol.called


def test_configure_dark_theme(gui_instance, mocker):
    """configure_dark_themeメソッドのテスト"""
    # 一度初期化されているので、ボタンやラベルを再設定
    gui_instance.root.configure.reset_mock()
    gui_instance.root.option_add.reset_mock()
    
    # テスト対象のメソッドを実行
    gui_instance.configure_dark_theme()
    
    # 確認
    assert gui_instance.root.configure.called
    assert gui_instance.root.option_add.call_count >= 2  # 2回以上呼ばれるはず


def test_hide_window(gui_instance):
    """hide_windowメソッドのテスト"""
    gui_instance.root.iconify.reset_mock()
    
    # テスト対象のメソッドを実行
    gui_instance.hide_window()
    
    # iconifyメソッドが呼ばれることを確認
    assert gui_instance.root.iconify.called


def test_show(gui_instance):
    """showメソッドのテスト"""
    gui_instance.root.deiconify.reset_mock()
    gui_instance.root.lift.reset_mock()
    gui_instance.root.focus_force.reset_mock()
    
    # テスト対象のメソッドを実行
    gui_instance.show()
    
    # 各メソッドが呼ばれることを確認
    assert gui_instance.root.deiconify.called
    assert gui_instance.root.lift.called
    assert gui_instance.root.focus_force.called


def test_quit(gui_instance):
    """quitメソッドのテスト"""
    gui_instance.root.quit.reset_mock()
    
    # テスト対象のメソッドを実行
    gui_instance.quit()
    
    # quitメソッドが呼ばれることを確認
    assert gui_instance.root.quit.called


def test_start_monitoring(gui_instance, mock_controller):
    """start_monitoringメソッドのテスト"""
    mock_controller.start.reset_mock()
    
    # テスト対象のメソッドを実行
    gui_instance.start_monitoring()
    
    # controllerのstartメソッドが呼ばれることを確認
    assert mock_controller.start.called


def test_stop_monitoring(gui_instance, mock_controller):
    """stop_monitoringメソッドのテスト"""
    mock_controller.stop.reset_mock()
    
    # テスト対象のメソッドを実行
    gui_instance.stop_monitoring()
    
    # controllerのstopメソッドが呼ばれることを確認
    assert mock_controller.stop.called


def test_exit_application(gui_instance, mock_controller):
    """exit_applicationメソッドのテスト"""
    mock_controller.exit.reset_mock()
    
    # テスト対象のメソッドを実行
    gui_instance.exit_application()
    
    # controllerのexitメソッドが呼ばれることを確認
    assert mock_controller.exit.called


def test_update_ui_on_start(gui_instance):
    """update_ui_on_startメソッドのテスト"""
    gui_instance.start_button.config = MagicMock()
    gui_instance.stop_button.config = MagicMock()
    gui_instance.status_label.config = MagicMock()
    
    # テスト対象のメソッドを実行
    gui_instance.update_ui_on_start()
    
    # UI要素が適切に更新されることを確認
    assert gui_instance.start_button.config.called
    assert gui_instance.stop_button.config.called
    assert gui_instance.status_label.config.called


def test_update_ui_on_stop(gui_instance):
    """update_ui_on_stopメソッドのテスト"""
    gui_instance.start_button.config = MagicMock()
    gui_instance.stop_button.config = MagicMock()
    gui_instance.status_label.config = MagicMock()
    
    # テスト対象のメソッドを実行
    gui_instance.update_ui_on_stop()
    
    # UI要素が適切に更新されることを確認
    assert gui_instance.start_button.config.called
    assert gui_instance.stop_button.config.called
    assert gui_instance.status_label.config.called


def test_update_ui_on_stop_with_message(gui_instance):
    """update_ui_on_stopメソッドのテスト - カスタムメッセージ指定"""
    gui_instance.start_button.config = MagicMock()
    gui_instance.stop_button.config = MagicMock()
    gui_instance.status_label.config = MagicMock()
    
    # テスト対象のメソッドをカスタムメッセージで実行
    custom_message = "カスタム停止メッセージ"
    gui_instance.update_ui_on_stop(message=custom_message)
    
    # UI要素が適切に更新されることを確認
    assert gui_instance.start_button.config.called
    assert gui_instance.stop_button.config.called
    assert gui_instance.status_label.config.called
    
    # キーワード引数を確認
    args, kwargs = gui_instance.status_label.config.call_args
    assert 'text' in kwargs
    assert kwargs['text'] == custom_message


def test_run(gui_instance):
    """runメソッドのテスト"""
    gui_instance.root.mainloop.reset_mock()
    
    # テスト対象のメソッドを実行
    gui_instance.run()
    
    # mainloopメソッドが呼ばれることを確認
    assert gui_instance.root.mainloop.called


def test_start_auto_detection(gui_instance, mocker):
    """start_auto_detectionメソッドのテスト"""
    # 初期化時に既に呼ばれている場合があるので、新たにモックを作り直す
    thread_mock = MagicMock()
    thread_mock.start = MagicMock()
    mocker.patch('threading.Thread', return_value=thread_mock)
    
    # テスト対象のメソッドを実行
    gui_instance.start_auto_detection()
    
    # スレッドが作成され、startメソッドが呼ばれることを確認
    assert thread_mock.start.called
