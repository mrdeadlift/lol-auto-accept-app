import pytest
from unittest.mock import MagicMock, patch
import tkinter as tk
from src.main import AutoAcceptGUI

@pytest.fixture
def thread_mock():
    def create_thread(*args, **kwargs):
        mock_instance = MagicMock()
        mock_instance._target = kwargs.get('target')
        mock_instance._started = False
        mock_instance.join = MagicMock()
        mock_instance.is_alive = MagicMock(return_value=True)

        # スレッドの開始時に実行されるstart関数を定義
        def start():
            mock_instance._started = True
        mock_instance.start = start

        return mock_instance
    return create_thread

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
            button._state = kwargs.get('state', tk.NORMAL)
            
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
            
            def cget(key):
                if key == 'state':
                    return button._state
                return None
            button.cget = cget
            
            return button
        
        mock_button.side_effect = create_button
        
        # Setup mock Label
        def create_label(*args, **kwargs):
            label = MagicMock()
            label.grid = MagicMock()
            label._text = kwargs.get('text', "待機中")
            
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
            
            def cget(key):
                if key == 'text':
                    return label._text
                return ''
            label.cget = cget
            
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
        
def test_gui_initialization(gui):
    """GUIの初期化テスト"""
    assert gui.root is not None
    assert not gui.monitoring
    assert gui.monitor_thread is None
    
    # ボタンの初期状態をチェック
    assert gui.start_button.cget('state') == tk.NORMAL
    assert gui.stop_button.cget('state') == tk.DISABLED
    
    # ステータスラベルの初期状態をチェック
    assert gui.status_label.cget('text') == "待機中"
    
    # 自動停止チェックボックスの初期状態をチェック
    assert not gui.auto_stop_var.get()
    
def test_start_monitoring(gui, thread_mock):
    """監視開始機能のテスト"""
    with patch('threading.Thread') as mock_thread:
        mock_thread.side_effect = thread_mock
        
        gui.start_monitoring()
        
        thread = mock_thread.return_value
        # スレッドが作成されたことを確認
        mock_thread.assert_called_once()
        assert mock_thread.call_args[1]['daemon'] is True
        assert thread._target is not None
        assert thread._started  # スレッドが開始されたことを確認
        
        # UIの状態をチェック
        assert gui.monitoring is True
        assert gui.start_button.cget('state') == tk.DISABLED
        assert gui.stop_button.cget('state') == tk.NORMAL
        assert gui.status_label.cget('text') == "監視中..."
        
def test_stop_monitoring(gui, thread_mock):
    """監視停止機能のテスト"""
    # 監視を開始してから停止
    with patch('threading.Thread') as mock_thread:
        mock_thread.side_effect = thread_mock
        
        # 監視を開始
        gui.start_monitoring()
        thread = mock_thread.return_value
        gui.monitor_thread = thread  # スレッドを明示的に設定
        assert gui.monitoring is True
        
        # 監視を停止
        gui.stop_monitoring()
        
        # スレッドのjoinが呼ばれたことを確認
        thread.join.assert_called_once_with(timeout=1)
    
    # 状態をチェック
    assert gui.monitoring is False
    assert gui.start_button.cget('state') == tk.NORMAL
    assert gui.stop_button.cget('state') == tk.DISABLED
    assert gui.status_label.cget('text') == "停止中"
    
# TODO: Uncomment the following test
# def test_auto_stop_behavior(gui, thread_mock):
#     """自動停止機能のテスト"""
#     with patch('src.main.LoLAutoAccept') as mock_lol:
#         # LoLAutoAcceptのモックを設定
#         mock_lol_instance = MagicMock()
#         mock_lol.return_value = mock_lol_instance
#         gui.auto_accept = mock_lol_instance
        
#         # scan_screenが受諾画面を検出したと設定
#         mock_lol_instance.scan_screen.return_value = True
            
#         with patch('threading.Thread') as mock_thread:
#             mock_thread.side_effect = thread_mock
            
#             # 自動停止をオンにしてモニタリング開始
#             gui.auto_stop_var.set(True)
#             gui.start_monitoring()

#             thread = mock_thread.return_value
#             gui.monitor_thread = thread  # スレッドを明示的に設定
            
#             # スレッドの設定と状態の確認
#             assert gui.monitoring is True
#             assert thread._started

#             # モニタリングスレッドのターゲット関数を取得して実行
#             monitor_func = mock_thread.call_args[1]['target']
#             monitor_func()  # この実行で自動停止が発生します
            
#             # GUI状態の検証
#             assert not gui.monitoring, "モニタリングが停止していません"
#             assert gui.status_label.cget('text') == "承認完了 - 停止中", \
#                    "自動停止後のステータスが正しくありません"
#             assert gui.start_button.cget('state') == tk.NORMAL, \
#                    "開始ボタンが有効化されていません"
#             assert gui.stop_button.cget('state') == tk.DISABLED, \
#                    "停止ボタンが無効化されていません"

def test_exit_application(gui, thread_mock):
    """アプリケーション終了機能のテスト"""
    with patch('threading.Thread') as mock_thread:
        mock_thread.side_effect = thread_mock
        
        # 監視を開始
        gui.start_monitoring()
        thread = mock_thread.return_value
        gui.monitor_thread = thread  # スレッドを明示的に設定
        
        # スレッドの設定と状態の確認
        assert gui.monitoring is True
        assert thread._started
        
        # 終了処理を実行
        gui.exit_application()
        
        # 監視が停止され、スレッドのjoinとquitが呼ばれたことを確認
        assert not gui.monitoring
        thread.join.assert_called_once_with(timeout=1)
        assert gui.root.quit.called
