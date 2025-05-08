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
    """Controlleru306eu30e2u30c3u30af"""
    controller = MagicMock()
    controller.monitoring = False
    controller.start = MagicMock()
    controller.stop = MagicMock()
    controller.exit = MagicMock()
    
    # auto_acceptu30d7u30edu30ddu30c6u30a3u306eu30e2u30c3u30af
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
def gui_instance(mock_controller, mock_tk, mocker):
    """AutoAcceptGUIu30a4u30f3u30b9u30bfu30f3u30b9u306eu4f5cu6210"""
    # u505cu6b62u72b6u614bu306eu30dcu30bfu30f3u3092u30e2u30c3u30af
    start_button = MagicMock()
    stop_button = MagicMock()
    status_label = MagicMock()
    
    # u30d1u30b9u95a2u9023u306eu30e2u30c3u30af
    mocker.patch('pathlib.Path.resolve', return_value=Path('/mock/path'))
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.path.join', return_value='/mock/path/resources/tray_icon.ico')
    
    # u30b9u30ecu30c3u30c9u95a2u9023u306eu30e2u30c3u30af
    thread_mock = MagicMock()
    thread_mock.start = MagicMock()
    mocker.patch('threading.Thread', return_value=thread_mock)
    
    # timeu3068u30edu30b0u306eu30e2u30c3u30af
    mocker.patch('time.sleep')
    mocker.patch('logging.info')
    mocker.patch('logging.error')
    mocker.patch('logging.warning')
    
    # tk.Tku3068u95a2u9023u30afu30e9u30b9u306eu632fu308bu821eu3044u3092u8a2du5b9a
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
    
    # AutoAcceptGUIu30a4u30f3u30b9u30bfu30f3u30b9u3092u4f5cu6210
    with patch('src.auto_accept_gui.tk.Button', side_effect=[start_button, stop_button]), \
         patch('src.auto_accept_gui.tk.Label', return_value=status_label):
        gui = AutoAcceptGUI(mock_controller)
        gui.start_button = start_button
        gui.stop_button = stop_button
        gui.status_label = status_label
        gui.root = root_mock
        gui.auto_monitor_thread = thread_mock
    
    return gui


def test_gui_initialization(gui_instance, mock_controller):
    """GUIu306eu521du671fu5316u30c6u30b9u30c8"""
    # u3053u306eu30c6u30b9u30c8u306fu30ecu30d9u30ebu306eu9ad8u3044u3082u306eu306au306eu3067u3001gui_instanceu306eu30d5u30a3u30afu30b9u30c1u30e3u306bu4f9du5b58u3057u3066u3044u308b
    # u30c6u30b9u30c8u7528u306bu5fc5u8981u306a assertions
    assert gui_instance.controller == mock_controller
    assert gui_instance.root is not None
    
    # rootu306eprotocolu30e1u30bdu30c3u30c9u304cWM_DELETE_WINDOWu3068hideu30e1u30bdu30c3u30c9u3092u767bu9332u3057u3066u3044u308bu3053u3068u3092u78bau8a8d
    gui_instance.root.protocol.assert_called_once()


def test_configure_dark_theme(gui_instance, mocker):
    """configure_dark_themeu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    # u4e00u5ea6u521du671fu5316u3055u308cu3066u3044u308bu306eu3067u3001u30dcu30bfu30f3u3084u30e9u30d9u30ebu3092u518du8a2du5b9a
    gui_instance.root.configure.reset_mock()
    gui_instance.root.option_add.reset_mock()
    
    # u30c6u30b9u30c8u5bfeu8c61u306eu30e1u30bdu30c3u30c9u3092u5b9fu884c
    gui_instance.configure_dark_theme()
    
    # u78bau8a8d
    gui_instance.root.configure.assert_called_once()
    assert gui_instance.root.option_add.call_count >= 2  # 2u56deu4ee5u4e0au547cu3070u308cu308bu306fu305a


def test_hide_window(gui_instance):
    """hide_windowu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    gui_instance.root.iconify.reset_mock()
    
    # u30c6u30b9u30c8u5bfeu8c61u306eu30e1u30bdu30c3u30c9u3092u5b9fu884c
    gui_instance.hide_window()
    
    # iconifyu30e1u30bdu30c3u30c9u304cu547cu3070u308cu308bu3053u3068u3092u78bau8a8d
    gui_instance.root.iconify.assert_called_once()


def test_show(gui_instance):
    """showu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    gui_instance.root.deiconify.reset_mock()
    gui_instance.root.lift.reset_mock()
    gui_instance.root.focus_force.reset_mock()
    
    # u30c6u30b9u30c8u5bfeu8c61u306eu30e1u30bdu30c3u30c9u3092u5b9fu884c
    gui_instance.show()
    
    # u5404u30e1u30bdu30c3u30c9u304cu547cu3070u308cu308bu3053u3068u3092u78bau8a8d
    gui_instance.root.deiconify.assert_called_once()
    gui_instance.root.lift.assert_called_once()
    gui_instance.root.focus_force.assert_called_once()


def test_quit(gui_instance):
    """quitu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    gui_instance.root.quit.reset_mock()
    
    # u30c6u30b9u30c8u5bfeu8c61u306eu30e1u30bdu30c3u30c9u3092u5b9fu884c
    gui_instance.quit()
    
    # quitu30e1u30bdu30c3u30c9u304cu547cu3070u308cu308bu3053u3068u3092u78bau8a8d
    gui_instance.root.quit.assert_called_once()


def test_start_monitoring(gui_instance, mock_controller):
    """start_monitoringu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    mock_controller.start.reset_mock()
    
    # u30c6u30b9u30c8u5bfeu8c61u306eu30e1u30bdu30c3u30c9u3092u5b9fu884c
    gui_instance.start_monitoring()
    
    # controlleru306estartu30e1u30bdu30c3u30c9u304cu547cu3070u308cu308bu3053u3068u3092u78bau8a8d
    mock_controller.start.assert_called_once()


def test_stop_monitoring(gui_instance, mock_controller):
    """stop_monitoringu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    mock_controller.stop.reset_mock()
    
    # u30c6u30b9u30c8u5bfeu8c61u306eu30e1u30bdu30c3u30c9u3092u5b9fu884c
    gui_instance.stop_monitoring()
    
    # controlleru306estopu30e1u30bdu30c3u30c9u304cu547cu3070u308cu308bu3053u3068u3092u78bau8a8d
    mock_controller.stop.assert_called_once()


def test_exit_application(gui_instance, mock_controller):
    """exit_applicationu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    mock_controller.exit.reset_mock()
    
    # u30c6u30b9u30c8u5bfeu8c61u306eu30e1u30bdu30c3u30c9u3092u5b9fu884c
    gui_instance.exit_application()
    
    # controlleru306eexitu30e1u30bdu30c3u30c9u304cu547cu3070u308cu308bu3053u3068u3092u78bau8a8d
    mock_controller.exit.assert_called_once()


def test_update_ui_on_start(gui_instance):
    """update_ui_on_startu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    gui_instance.start_button.config = MagicMock()
    gui_instance.stop_button.config = MagicMock()
    gui_instance.status_label.config = MagicMock()
    
    # u30c6u30b9u30c8u5bfeu8c61u306eu30e1u30bdu30c3u30c9u3092u5b9fu884c
    gui_instance.update_ui_on_start()
    
    # UIu8981u7d20u304cu9069u5207u306bu66f4u65b0u3055u308cu308bu3053u3068u3092u78bau8a8d
    gui_instance.start_button.config.assert_called_once()
    gui_instance.stop_button.config.assert_called_once()
    gui_instance.status_label.config.assert_called_once()


def test_update_ui_on_stop(gui_instance):
    """update_ui_on_stopu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    gui_instance.start_button.config = MagicMock()
    gui_instance.stop_button.config = MagicMock()
    gui_instance.status_label.config = MagicMock()
    
    # u30c6u30b9u30c8u5bfeu8c61u306eu30e1u30bdu30c3u30c9u3092u5b9fu884c
    gui_instance.update_ui_on_stop()
    
    # UIu8981u7d20u304cu9069u5207u306bu66f4u65b0u3055u308cu308bu3053u3068u3092u78bau8a8d
    gui_instance.start_button.config.assert_called_once()
    gui_instance.stop_button.config.assert_called_once()
    gui_instance.status_label.config.assert_called_once()


def test_update_ui_on_stop_with_message(gui_instance):
    """update_ui_on_stopu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8 - u30abu30b9u30bfu30e0u30e1u30c3u30bbu30fcu30b8u6307u5b9a"""
    gui_instance.start_button.config = MagicMock()
    gui_instance.stop_button.config = MagicMock()
    gui_instance.status_label.config = MagicMock()
    
    # u30c6u30b9u30c8u5bfeu8c61u306eu30e1u30bdu30c3u30c9u3092u30abu30b9u30bfu30e0u30e1u30c3u30bbu30fcu30b8u3067u5b9fu884c
    custom_message = "u30abu30b9u30bfu30e0u505cu6b62u30e1u30c3u30bbu30fcu30b8"
    gui_instance.update_ui_on_stop(message=custom_message)
    
    # UIu8981u7d20u304cu9069u5207u306bu66f4u65b0u3055u308cu308bu3053u3068u3092u78bau8a8d
    gui_instance.start_button.config.assert_called_once()
    gui_instance.stop_button.config.assert_called_once()
    gui_instance.status_label.config.assert_called_once()
    
    # u30adu30fcu30efu30fcu30c9u5f15u6570u3092u78bau8a8d
    args, kwargs = gui_instance.status_label.config.call_args
    assert 'text' in kwargs
    assert kwargs['text'] == custom_message


def test_run(gui_instance):
    """runu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    gui_instance.root.mainloop.reset_mock()
    
    # u30c6u30b9u30c8u5bfeu8c61u306eu30e1u30bdu30c3u30c9u3092u5b9fu884c
    gui_instance.run()
    
    # mainloopu30e1u30bdu30c3u30c9u304cu547cu3070u308cu308bu3053u3068u3092u78bau8a8d
    gui_instance.root.mainloop.assert_called_once()


def test_start_auto_detection(gui_instance, mocker):
    """start_auto_detectionu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    # u521du671fu5316u6642u306bu65e2u306bu547cu3070u308cu3066u3044u308bu53reu304cu3042u308bu306eu3067u3001u65b0u305fu306bu30dau30c3u30c8u3092u4f5cu308au76f4u3059
    thread_mock = MagicMock()
    thread_mock.start = MagicMock()
    mocker.patch('threading.Thread', return_value=thread_mock)
    
    # u30c6u30b9u30c8u5bfeu8c61u306eu30e1u30bdu30c3u30c9u3092u5b9fu884c
    gui_instance.start_auto_detection()
    
    # u30b9u30ecu30c3u30c9u304cu4f5cu6210u3055u308cu3001startu30e1u30bdu30c3u30c9u304cu547cu3070u308cu308bu3053u3068u3092u78bau8a8d
    thread_mock.start.assert_called_once()
