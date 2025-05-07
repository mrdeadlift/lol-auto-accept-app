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
    """Controlleru306eu30e2u30c3u30af"""
    controller = MagicMock()
    controller.monitoring = False
    controller.start = MagicMock()
    controller.stop = MagicMock()
    controller.exit = MagicMock()
    controller.show_window = MagicMock()
    return controller


@pytest.fixture
def tray_icon_instance(mock_controller, mock_pystray, mocker):
    """TrayIconu30a4u30f3u30b9u30bfu30f3u30b9u306eu4f5cu6210"""
    # u30d1u30b9u95a2u9023u306eu30e2u30c3u30af
    mocker.patch('pathlib.Path.resolve', return_value=Path('/mock/path'))
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.path.join', return_value='/mock/path/resources/tray_icon.png')
    
    # Pillow Image.openu306eu30e2u30c3u30af
    image_mock = MagicMock(spec=Image.Image)
    mocker.patch('PIL.Image.open', return_value=image_mock)
    
    # u30b9u30ecu30c3u30c9u3068u30edu30b0u306eu30e2u30c3u30af
    thread_mock = MagicMock()
    thread_mock.start = MagicMock()
    mocker.patch('threading.Thread', return_value=thread_mock)
    mocker.patch('logging.info')
    mocker.patch('logging.error')
    mocker.patch('logging.warning')
    
    # PyStray Menu u95a2u9023u306eu30e2u30c3u30af
    menu_mock = MagicMock()
    mocker.patch('pystray.Menu', return_value=menu_mock)
    
    # TrayIcon u30a4u30f3u30b9u30bfu30f3u30b9u3092u4f5cu6210
    tray_icon = TrayIcon(mock_controller)
    tray_icon.tray_thread = thread_mock
    
    return tray_icon


def test_init_with_default_icon(mock_controller, mock_pystray, mocker):
    """u30c7u30d5u30a9u30ebu30c8u30a2u30a4u30b3u30f3u3067u306eu521du671fu5316u30c6u30b9u30c8"""
    # u30d1u30b9u95a2u9023u306eu30e2u30c3u30af
    mocker.patch('pathlib.Path.resolve', return_value=Path('/mock/path'))
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.path.join', return_value='/mock/path/resources/tray_icon.png')
    
    # Imageu30e2u30c3u30af
    image_mock = MagicMock(spec=Image.Image)
    mocker.patch('PIL.Image.open', return_value=image_mock)
    
    # u30edu30b0u306eu30e2u30c3u30af
    log_info_mock = mocker.patch('logging.info')
    
    # TrayIconu3092u4f5cu6210
    tray_icon = TrayIcon(mock_controller)
    
    # u78bau8a8d
    assert tray_icon.controller == mock_controller
    assert tray_icon.is_monitoring == mock_controller.monitoring
    assert hasattr(tray_icon, 'icon')
    assert log_info_mock.called


def test_init_with_custom_icon(mock_controller, mock_pystray, mocker):
    """u30abu30b9u30bfu30e0u30a2u30a4u30b3u30f3u3067u306eu521du671fu5316u30c6u30b9u30c8"""
    # Imageu30e2u30c3u30af
    image_mock = MagicMock(spec=Image.Image)
    mocker.patch('PIL.Image.open', return_value=image_mock)
    
    # u81eau4f5cu30a2u30a4u30b3u30f3u30d1u30b9
    custom_icon_path = '/custom/icon/path.png'
    
    # TrayIconu3092u30abu30b9u30bfu30e0u30a2u30a4u30b3u30f3u3067u4f5cu6210
    tray_icon = TrayIcon(mock_controller, icon_path=custom_icon_path)
    
    # u78bau8a8d
    mock_pystray['icon'].assert_called_once()
    image_open_calls = mocker.patch('PIL.Image.open').call_args_list
    assert len(image_open_calls) > 0
    assert image_open_calls[0][0][0] == custom_icon_path


def test_init_no_icon_found(mock_controller, mock_pystray, mocker):
    """u30a2u30a4u30b3u30f3u304cu898bu3064u304bu3089u306au3044u5834u5408u306eu521du671fu5316u30c6u30b9u30c8"""
    # u6700u521du306eu30d1u30b9u304cu5b58u5728u3057u306au3044u304cu3001resourcesu5185u306b1u3064u306fPNGu304cu3042u308bu72b6u6cc1u3092u30e2u30c3u30af
    mocker.patch('pathlib.Path.resolve', return_value=Path('/mock/path'))
    
    def path_exists_side_effect(path):
        if path == '/mock/path/resources/tray_icon.png':
            return False
        else:
            return True
    
    mocker.patch('os.path.exists', side_effect=path_exists_side_effect)
    mocker.patch('os.path.join', side_effect=lambda *args: '/'.join(args))
    
    # resourcesu30c7u30a3u30ecu30afu30c8u30eau5185u306eu30d5u30a1u30a4u30ebu3092u30e2u30c3u30af
    def listdir_side_effect(path):
        if path == '/mock/path/resources':
            return ['alternative.png']
        return []
    
    mocker.patch('os.listdir', side_effect=listdir_side_effect)
    
    # Imageu30e2u30c3u30af
    image_mock = MagicMock(spec=Image.Image)
    mocker.patch('PIL.Image.open', return_value=image_mock)
    
    # u30edu30b0u306eu30e2u30c3u30af
    log_warning_mock = mocker.patch('logging.warning')
    log_info_mock = mocker.patch('logging.info')
    
    # TrayIconu3092u4f5cu6210
    tray_icon = TrayIcon(mock_controller)
    
    # u78bau8a8d
    assert log_warning_mock.called
    assert log_info_mock.called
    assert hasattr(tray_icon, 'icon')


def test_create_menu(tray_icon_instance, mock_pystray):
    """u30e1u30cbu30e5u30fcu4f5cu6210u306eu30c6u30b9u30c8"""
    # _create_menu u3092u547cu3073u51fau3059
    menu = tray_icon_instance._create_menu()
    
    # PyStray.Menu u304cu547cu3070u308cu305fu3053u3068u3092u78bau8a8d
    assert mock_pystray['menu'] == menu
    assert mock_pystray['menu_item'].call_count >= 4  # 4u3064u4ee5u4e0au306eu30e1u30cbu30e5u30fcu30a2u30a4u30c6u30e0


def test_handle_open(tray_icon_instance, mock_controller):
    """_handle_openu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    # _handle_open u3092u547cu3073u51fau3059
    tray_icon_instance._handle_open()
    
    # controlleru306eshow_windowu304cu547cu3070u308cu305fu3053u3068u3092u78bau8a8d
    mock_controller.show_window.assert_called_once()


def test_handle_start(tray_icon_instance, mock_controller):
    """_handle_startu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    # _handle_start u3092u547cu3073u51fau3059
    tray_icon_instance._handle_start()
    
    # controlleru306estartu304cu547cu3070u308cu305fu3053u3068u3092u78bau8a8d
    mock_controller.start.assert_called_once()


def test_handle_stop(tray_icon_instance, mock_controller):
    """_handle_stopu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    # _handle_stop u3092u547cu3073u51fau3059
    tray_icon_instance._handle_stop()
    
    # controlleru306estopu304cu547cu3070u308cu305fu3053u3068u3092u78bau8a8d
    mock_controller.stop.assert_called_once()


def test_handle_exit(tray_icon_instance, mock_controller):
    """_handle_exitu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    # _handle_exit u3092u547cu3073u51fau3059
    tray_icon_instance._handle_exit()
    
    # shutdown u304cu547cu3070u308cu305fu3053u3068u3092u78bau8a8d
    assert mock_controller.exit.called


def test_update_menu_state(tray_icon_instance, mocker):
    """update_menu_stateu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    # u5fc5u8981u306au30e2u30c3u30af
    log_info_mock = mocker.patch('logging.info')
    
    # u521du671fu72b6u614bu3092u78bau8a8d
    assert tray_icon_instance.is_monitoring is False
    
    # update_menu_state u3092u547cu3073u51fau3059
    tray_icon_instance.update_menu_state(True)
    
    # u72b6u614bu304cu66f4u65b0u3055u308cu305fu3053u3068u3092u78bau8a8d
    assert tray_icon_instance.is_monitoring is True
    assert log_info_mock.called


def test_run(tray_icon_instance):
    """runu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    # runu30e1u30bdu30c3u30c9u3092u547cu3073u51fau3059
    tray_icon_instance.run()
    
    # u30b9u30ecu30c3u30c9u304cu958bu59cbu3055u308cu305fu3053u3068u3092u78bau8a8d
    tray_icon_instance.tray_thread.start.assert_called_once()


def test_shutdown(tray_icon_instance, mock_pystray):
    """shutdownu30e1u30bdu30c3u30c9u306eu30c6u30b9u30c8"""
    # shutdownu30e1u30bdu30c3u30c9u3092u547cu3073u51fau3059
    tray_icon_instance.shutdown()
    
    # iconu306estopu30e1u30bdu30c3u30c9u304cu547cu3070u308cu305fu3053u3068u3092u78bau8a8d
    mock_pystray['icon'].stop.assert_called_once()


def test_shutdown_exception(tray_icon_instance, mock_pystray, mocker):
    """shutdownu30e1u30bdu30c3u30c9u306eu4f8bu5916u30c6u30b9u30c8"""
    # stopu30e1u30bdu30c3u30c9u304cu4f8bu5916u3092u6295u3052u308bu3088u3046u306bu8a2du5b9a
    mock_pystray['icon'].stop.side_effect = Exception("Stop error")
    
    # u30edu30b0u306eu30e2u30c3u30af
    log_error_mock = mocker.patch('logging.error')
    
    # shutdownu30e1u30bdu30c3u30c9u3092u547cu3073u51fau3059
    tray_icon_instance.shutdown()
    
    # u30a8u30e9u30fcu30edu30b0u304cu8a18u9332u3055u308cu305fu3053u3068u3092u78bau8a8d
    assert log_error_mock.called
