import pyautogui
import cv2
import time
from PIL import ImageGrab
import logging
import sys
import os
import tkinter as tk
from tkinter import ttk
import threading
from pathlib import Path
import json
import argparse
from controller import Controller
from tray_icon import TrayIcon

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_config_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / 'config.json'
    else:
        return Path(__file__).resolve().parent.parent / 'config.json'

def load_config():
    path = get_config_path()
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            logging.error(f"設定ファイル読み込み失敗: {e}")
    try:
        path.write_text(json.dumps(DEFAULT_CONFIG, indent=4), encoding='utf-8')
        logging.info(f"デフォルト設定作成: {path}")
    except Exception as e:
        logging.error(f"設定ファイル作成失敗: {e}")
    return DEFAULT_CONFIG.copy()

def save_config(config):
    path = get_config_path()
    try:
        path.write_text(json.dumps(config, indent=4), encoding='utf-8')
        logging.info(f"設定ファイル保存: {path}")
    except Exception as e:
        logging.error(f"設定ファイル保存失敗: {e}")

class LoLAutoAccept:
    def __init__(self, config=None):
        pyautogui.FAILSAFE = True
        self.config = config or load_config()
        self.button_image = self.config['images']['accept_button']
        # イメージフォルダ
        if getattr(sys, 'frozen', False):
            image_dir = sys._MEIPASS
        else:
            image_dir = str(Path(__file__).resolve().parent.parent)
        abs_path = os.path.join(image_dir, self.button_image)
        if not os.path.exists(abs_path):
            logging.error(f"ボタン画像が見つかりません: {abs_path}")
            sys.exit(1)
        logging.info(f"ボタン画像読み込み: {self.button_image}")
        self.button_image_path = abs_path
        self.confidence = self.config['template_matching']['confidence']
        self.interval_sec = self.config['template_matching']['interval_sec']
        self.last_error_time = 0
        self.error_cooldown = 60

    def scan_screen(self):
        """画面をスキャンしてマッチング画面の承認ボタンを探す"""
        try:
            # 画面上でボタン画像を探す（より寛容なマッチング）
            button_pos = pyautogui.locateOnScreen(self.button_image_path, confidence=self.confidence)
            
            if button_pos is not None:
                # ボタンが見つかった場合、中央をクリック
                center = pyautogui.center(button_pos)
                pyautogui.click(center)
                logging.info("承認ボタンをクリックしました")
                # クリック後に少し待機
                time.sleep(2)
                return True
            return False
            
        except pyautogui.ImageNotFoundException:
            # 画像が見つからない場合は正常な状態なのでエラーとして扱わない
            return False
        except Exception as e:
            current_time = time.time()
            # エラーログの出力を制限する
            if current_time - self.last_error_time >= self.error_cooldown:
                logging.error(f"エラーが発生しました: {str(e)}")
                self.last_error_time = current_time
            return False

    def run(self):
        """メインループ"""
        logging.info("LoL Auto Accept を開始しました")
        try:
            while True:
                self.scan_screen()
                # 負荷軽減のため少し待機
                time.sleep(self.interval_sec)
        
        except KeyboardInterrupt:
            logging.info("プログラムを終了します")
        except Exception as e:
            logging.error(f"予期せぬエラーが発生しました: {str(e)}")
            logging.info("プログラムを終了します")

class AutoAcceptGUI:
    def __init__(self, controller=None):
        self.root = tk.Tk()
        self.root.title("LoL Auto Accept")
        self.root.geometry("300x250")  # ウィンドウサイズを少し大きくします
        
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ボタン
        self.start_button = ttk.Button(main_frame, text="開始", command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_button = ttk.Button(main_frame, text="停止", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)

        # 自動停止チェックボックス
        self.auto_stop_var = tk.BooleanVar(value=True)
        self.auto_stop_checkbox = ttk.Checkbutton(main_frame, text="自動で停止する", variable=self.auto_stop_var)
        self.auto_stop_checkbox.grid(row=1, column=0, columnspan=2, pady=5)
        
        # 自動開始チェックボックス
        self.auto_start_var = tk.BooleanVar(value=True)  # デフォルトでオン
        self.auto_start_checkbox = ttk.Checkbutton(main_frame, text="マッチング時に自動開始", variable=self.auto_start_var)
        self.auto_start_checkbox.grid(row=2, column=0, columnspan=2, pady=5)
        
        self.exit_button = ttk.Button(main_frame, text="終了", command=self.exit_application)
        self.exit_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # ステータスラベル
        self.status_label = ttk.Label(main_frame, text="待機中")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        try:
            # Use provided controller or create a new one
            if controller is None:
                self.auto_accept = LoLAutoAccept()
                self.controller = Controller(self.auto_accept, self)
            else:
                self.controller = controller
                self.auto_accept = controller.auto_accept
            
            # Configure window close event to hide instead of quit
            self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
            
            # Start auto detection
            self.start_auto_detection()
        except Exception as e:
            logging.error(f"GUIの初期化中にエラーが発生しました: {str(e)}")
            self.root.destroy()
            sys.exit(1)

    def start_auto_detection(self):
        """マッチング画像の検出を監視し、検出時に自動で監視を開始するスレッド"""
        def auto_detect():
            logging.info("自動検出を開始しました")
            rel = self.auto_accept.config['images']['matching_screen']
            base = getattr(self.auto_accept, 'button_image_path', '')
            image_dir = os.path.dirname(base) if base else os.getcwd()
            matching_image_path = os.path.join(image_dir, rel)
            
            # 画像ファイルの存在確認
            if not os.path.exists(matching_image_path):
                logging.error(f"マッチング画像が見つかりません: {matching_image_path}")
            else:
                logging.info(f"マッチング画像を読み込みました: {matching_image_path}")
            
            while self.controller.running:
                try:
                    # ファイルの存在を毎回確認
                    if not os.path.exists(matching_image_path):
                        time.sleep(5)  # ファイルがない場合は5秒待機
                        continue
                        
                    if not self.controller.monitoring and self.auto_start_var.get():
                        # マッチング画像を検出
                        matching_pos = pyautogui.locateOnScreen(matching_image_path, confidence=self.auto_accept.confidence)
                        if matching_pos is not None:
                            logging.info("マッチング画面を検出しました。自動監視を開始します。")
                            # GUIスレッドから実行するために、after()を使用
                            self.root.after(0, self.start_monitoring)
                except pyautogui.ImageNotFoundException:
                    # 画像が見つからない場合は正常な状態なのでログ出力しない
                    pass
                except FileNotFoundError as e:
                    logging.error(f"画像ファイルが見つかりません: {str(e)}")
                    time.sleep(10)  # エラー発生時は長めの待機
                except Exception as e:
                    import traceback
                    logging.error(f"自動検出中にエラーが発生しました: {str(e)}")
                    logging.error(traceback.format_exc())  # スタックトレースを出力
                    time.sleep(5)  # エラー発生時は長めの待機
                
                time.sleep(self.auto_accept.interval_sec)  # 設定間隔で検出
        
        self.auto_monitor_thread = threading.Thread(target=auto_detect, daemon=True)
        self.auto_monitor_thread.start()
        
    def start_monitoring(self):
        self.controller.start()
        
    def update_ui_on_start(self):
        """Called by controller when monitoring starts"""
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="監視中...")

    def stop_monitoring(self):
        self.controller.stop()
        
    def update_ui_on_stop(self, message="停止中"):
        """Called by controller when monitoring stops"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text=message)

    def exit_application(self):
        self.controller.exit()

    def hide_window(self):
        """Hide the window instead of quitting the application"""
        self.root.withdraw()
        
    def show(self):
        """Show the window and bring it to front"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit(self):
        """Quit the application"""
        self.root.quit()

    def load_settings(self):
        cfg = load_config()
        # 設定反映
        self.auto_accept.config = cfg
        self.auto_accept.confidence = cfg['template_matching']['confidence']
        self.auto_accept.interval_sec = cfg['template_matching']['interval_sec']
        self.status_label.config(text="設定をリロードしました")

    def save_settings(self):
        save_config(self.auto_accept.config)
        self.status_label.config(text="設定を保存しました")

    def run(self):
        self.root.mainloop()

# Define DEFAULT_CONFIG if it doesn't exist
DEFAULT_CONFIG = {
    "images": {
        "accept_button": "accept_button.png",
        "matching_screen": "matching.png"
    },
    "template_matching": {
        "confidence": 0.7,
        "interval_sec": 1.0
    }
}

def parse_arguments():
    parser = argparse.ArgumentParser(description='LoL Auto Accept - マッチングの自動承認ツール')
    parser.add_argument('--nogui', action='store_true', help='GUIを表示せずにバックグラウンドで実行')
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Create the auto accept instance
    auto_accept = LoLAutoAccept()
    
    if args.nogui:
        # Run in background mode without GUI
        controller = Controller(auto_accept)
        tray_icon = TrayIcon(controller)
        tray_icon.run()
        
        # Start monitoring automatically in nogui mode
        controller.start()
        
        # Keep the main thread alive
        try:
            while controller.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("キーボード割り込みによりプログラムを終了します")
        finally:
            controller.exit()
    else:
        # Run with GUI
        controller = Controller(auto_accept)
        gui = AutoAcceptGUI(controller)
        
        # Set the controller's GUI reference
        controller.gui = gui
        
        # Create and run the tray icon
        tray_icon = TrayIcon(controller)
        tray_icon.run()
        
        # Run the GUI
        gui.run()
        
        # Clean up tray icon when GUI exits
        try:
            tray_icon.shutdown()
        except Exception as e:
            logging.error(f"終了時にエラーが発生しました: {str(e)}")
