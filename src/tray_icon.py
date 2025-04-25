import pystray
from PIL import Image
from threading import Thread
import logging
import os
from pathlib import Path

class TrayIcon:
    def __init__(self, controller, icon_path=None):
        self.controller = controller
        
        # Default icon path if not provided
        if icon_path is None:
            if getattr(import_sys := __import__('sys'), 'frozen', False):
                base_dir = import_sys._MEIPASS
            else:
                base_dir = str(Path(__file__).resolve().parent.parent)
            icon_path = os.path.join(base_dir, 'resources', 'tray_icon.png')
        
        # Check if icon exists
        if not os.path.exists(icon_path):
            logging.warning(f"トレイアイコンが見つかりません: {icon_path}")
            # Try to find any PNG in resources
            resources_dir = os.path.join(base_dir, 'resources')
            if os.path.exists(resources_dir):
                for file in os.listdir(resources_dir):
                    if file.endswith('.png'):
                        icon_path = os.path.join(resources_dir, file)
                        logging.info(f"代替アイコンを使用します: {icon_path}")
                        break
        
        try:
            self.icon = pystray.Icon(
                'lol_auto_accept', 
                Image.open(icon_path), 
                'LoL Auto Accept', 
                menu=self._build_menu()
            )
            logging.info(f"トレイアイコンを初期化しました: {icon_path}")
        except Exception as e:
            logging.error(f"トレイアイコンの初期化に失敗しました: {str(e)}")
            raise
    
    def _build_menu(self):
        return pystray.Menu(
            pystray.MenuItem('開く', self._handle_open),
            pystray.MenuItem('開始', self._handle_start),
            pystray.MenuItem('停止', self._handle_stop),
            pystray.MenuItem('終了', self._handle_exit)
        )
    
    def _handle_open(self):
        self.controller.show_window()
    
    def _handle_start(self):
        self.controller.start()
    
    def _handle_stop(self):
        self.controller.stop()
    
    def _handle_exit(self):
        self.shutdown()
        self.controller.exit()
    
    def run(self):
        """Run the tray icon in a separate thread"""
        self.tray_thread = Thread(target=self.icon.run, daemon=True)
        self.tray_thread.start()
        logging.info("システムトレイアイコンを起動しました")
    
    def shutdown(self):
        """Stop the tray icon"""
        try:
            if hasattr(self, 'icon'):
                self.icon.stop()
                logging.info("システムトレイアイコンを停止しました")
        except Exception as e:
            logging.error(f"トレイアイコンの停止中にエラーが発生しました: {str(e)}")
