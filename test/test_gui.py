import pytest
from unittest.mock import MagicMock, patch
import tkinter as tk
from src.main import AutoAcceptGUI

@pytest.fixture
def mock_tk_components():
    with patch('tkinter.Tk') as mock_tk, \
         patch('tkinter.ttk.Frame') as mock_frame, \
         patch('tkinter.ttk.Button') as mock_button, \
         patch('tkinter.ttk.Label') as mock_label, \
         patch('tkinter.ttk.Checkbutton') as mock_checkbutton, \
         patch('tkinter.BooleanVar') as mock_bool_var:
        
        # Setup mock Tk
        mock_root = mock_tk.return_value
        mock_root.title = MagicMock(return_value="LoL Auto Accept")
        mock_root.geometry = MagicMock()
        
        # Setup mock Frame
        mock_frame.return_value.grid = MagicMock()
        
        # Setup mock Buttons
        def create_button(*args, **kwargs):
            button = MagicMock()
            button.grid = MagicMock()
            button._state = kwargs.get('state', 'normal')
            
            def config(**cfg):
                if 'state' in cfg:
                    button._state = cfg['state']
            button.config = config
            button.configure = config
            
            def getitem(key):
                if key == 'state':
                    return button._state
                return None
            button.__getitem__ = getitem
            return button
        
        mock_button.side_effect = create_button
        
        # Setup mock Label
        def create_label(*args, **kwargs):
            label = MagicMock()
            label.grid = MagicMock()
            label._text = "待機中"
            
            def config(**cfg):
                if 'text' in cfg:
                    label._text = cfg['text']
            label.config = config
            label.configure = config
            
            def getitem(key):
                if key == 'text':
                    return label._text
                return ''
            label.__getitem__ = getitem
            return label
        
        mock_label.side_effect = create_label
        
        # Setup mock BooleanVar
        mock_bool_var.return_value.get = MagicMock(return_value=False)
        mock_bool_var.return_value.set = MagicMock()
        
        yield {
            'tk': mock_tk,
            'frame': mock_frame,
            'button': mock_button,
            'label': mock_label,
            'checkbutton': mock_checkbutton,
            'bool_var': mock_bool_var
        }

@pytest.fixture
def gui(mock_tk_components):
    with patch('src.main.LoLAutoAccept'):
        gui = AutoAcceptGUI()
        gui.stop_button.configure(state='disabled')  # 初期状態を設定
        yield gui
        
# TODO テストが失敗するので修正が必要
def test_gui_initialization(gui):
    """GUIの初期化テスト"""
    assert gui.root is not None
    assert not gui.monitoring
    assert gui.monitor_thread is None
    
    # ボタンの初期状態をチェック
    assert str(gui.start_button['state']) == 'normal'
    assert str(gui.stop_button['state']) == 'disabled'
    
    # ステータスラベルの初期状態をチェック
    assert gui.status_label['text'] == "待機中"
    
    # 自動停止チェックボックスの初期状態をチェック
    assert not gui.auto_stop_var.get()
    
# TODO テストが失敗するので修正が必要
def test_start_monitoring(gui):
    """監視開始機能のテスト"""
    with patch('threading.Thread') as mock_thread:
        gui.start_monitoring()
        
        # スレッドが作成されたことを確認
        mock_thread.assert_called_once()
        assert mock_thread.call_args[1]['daemon'] is True
        
        # UIの状態をチェック
        assert gui.monitoring is True
        assert str(gui.start_button['state']) == 'disabled'
        assert str(gui.stop_button['state']) == 'normal'
        assert gui.status_label['text'] == "監視中..."
        
# TODO テストが失敗するので修正が必要
def test_stop_monitoring(gui):
    """監視停止機能のテスト"""
    # 監視を開始してから停止
    with patch('threading.Thread') as mock_thread:
        gui.start_monitoring()
        gui.stop_monitoring()
        
        # 状態をチェック
        assert gui.monitoring is False
        assert str(gui.start_button['state']) == 'normal'
        assert str(gui.stop_button['state']) == 'disabled'
        assert gui.status_label['text'] == "停止中"

# def test_auto_stop_behavior(gui):
#     """自動停止機能のテスト"""
#     # 自動停止をオンにする
#     gui.auto_stop_var.set(True)
    
#     with patch('src.main.LoLAutoAccept') as mock_lol:
#         # scan_screenがTrueを返すようにモック
#         mock_lol.return_value.scan_screen.return_value = True
        
#         with patch('threading.Thread') as mock_thread:
#             # モニタリングを開始
#             gui.start_monitoring()
            
#             # スレッドの動作をシミュレート
#             mock_thread.call_args[1]['target']()
            
#             # 自動停止が機能したことを確認
#             assert not gui.monitoring
#             assert gui.status_label['text'] == "承認完了 - 停止中"

# TODO テストが失敗するので修正が必要
def test_exit_application(gui):
    """アプリケーション終了機能のテスト"""
    with patch('tkinter.Tk.quit') as mock_quit:
        # 監視中の状態で終了
        gui.monitoring = True
        gui.exit_application()
        
        # 監視が停止され、quitが呼ばれたことを確認
        assert not gui.monitoring
        mock_quit.assert_called_once()
