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

def get_log_path():
    """実行環境に応じてログファイルのパスを取得"""
    if getattr(sys, 'frozen', False):
        # exe実行時はexeと同じディレクトリにログを作成
        return os.path.join(os.path.dirname(sys.executable), 'app.log')
    else:
        # 通常実行時はカレントディレクトリにログを作成
        return 'app.log'

# ログの設定
try:
    log_path = get_log_path()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_path, encoding='utf-8')
        ]
    )
except Exception as e:
    # ログファイルの作成に失敗した場合は標準出力のみ使用
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logging.warning(f"ログファイルの作成に失敗しました: {str(e)}")

class LoLAutoAccept:
    def __init__(self):
        # pyautoguiの設定
        pyautogui.FAILSAFE = True  # 画面端にマウスを移動で停止
        
        try:
            # 実行ファイルかソースコードかを判断してパスを設定
            if getattr(sys, 'frozen', False):
                # exe実行時の画像パスの探索順序
                possible_paths = [
                    os.path.join(sys._MEIPASS, 'accept_button.png'),
                    os.path.join(os.path.dirname(sys.executable), 'accept_button.png'),
                    os.path.join(os.getcwd(), 'accept_button.png')
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        self.button_image = path
                        break
                else:
                    raise FileNotFoundError("ボタン画像が見つかりませんでした")
            else:
                # ソースコード実行時
                application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.button_image = os.path.join(application_path, 'accept_button.png')
                if not os.path.exists(self.button_image):
                    raise FileNotFoundError(f"ボタン画像が見つかりません: {self.button_image}")
            
            logging.info(f"ボタン画像を読み込みました: {self.button_image}")
                
        except Exception as e:
            logging.error(f"初期化中にエラーが発生しました: {str(e)}")
            sys.exit(1)
        
        # エラーログの制御用変数
        self.last_error_time = 0
        self.error_cooldown = 60  # エラーログの出力間隔（秒）

    def scan_screen(self):
        """画面をスキャンしてマッチング画面の承認ボタンを探す"""
        try:
            # 画面上でボタン画像を探す（より寛容なマッチング）
            button_pos = pyautogui.locateOnScreen(self.button_image, confidence=0.7)
            
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
                time.sleep(1)
        
        except KeyboardInterrupt:
            logging.info("プログラムを終了します")
        except Exception as e:
            logging.error(f"予期せぬエラーが発生しました: {str(e)}")
            logging.info("プログラムを終了します")

class AutoAcceptGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LoL Auto Accept")
        self.root.geometry("300x200")  # ウィンドウサイズを少し大きくします
        
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
            self.auto_accept = LoLAutoAccept()
            self.monitoring = False
            self.monitor_thread = None
            self.auto_monitor_thread = None
            
            # 自動監視の有効化
            self.start_auto_detection()
        except Exception as e:
            logging.error(f"GUIの初期化中にエラーが発生しました: {str(e)}")
            self.root.destroy()
            sys.exit(1)

    def start_auto_detection(self):
        """マッチング画像の検出を監視し、検出時に自動で監視を開始するスレッド"""
        def auto_detect():
            logging.info("自動検出を開始しました")
            # マッチング画像のパスを設定
            matching_image_path = r"C:\Users\owner\Documents\projects\lol-auto-apply-app\matching.png"
            
            # 画像ファイルの存在確認
            if not os.path.exists(matching_image_path):
                logging.error(f"マッチング画像が見つかりません: {matching_image_path}")
            else:
                logging.info(f"マッチング画像を読み込みました: {matching_image_path}")
            
            while True:
                try:
                    # ファイルの存在を毎回確認
                    if not os.path.exists(matching_image_path):
                        time.sleep(5)  # ファイルがない場合は5秒待機
                        continue
                        
                    if not self.monitoring and self.auto_start_var.get():
                        # マッチング画像を検出
                        matching_pos = pyautogui.locateOnScreen(matching_image_path, confidence=0.7)
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
                
                time.sleep(2)  # 2秒間隔で検出
        
        self.auto_monitor_thread = threading.Thread(target=auto_detect, daemon=True)
        self.auto_monitor_thread.start()
        
    def start_monitoring(self):
        self.monitoring = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="監視中...")
        
        def monitor():
            while self.monitoring:
                try:
                    is_accepted = self.auto_accept.scan_screen() and self.auto_stop_var.get()
                    if is_accepted:
                        # Set monitoring to false first to avoid recursion in stop_monitoring
                        self.monitoring = False
                        self.status_label.config(text="承認完了 - 停止中")
                        self.start_button.config(state=tk.NORMAL)
                        self.stop_button.config(state=tk.DISABLED)
                        break
                except Exception as e:
                    logging.error(f"監視中にエラーが発生しました: {str(e)}")
                time.sleep(1)
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=1)
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text="停止中")

    def exit_application(self):
        if self.monitoring:
            self.stop_monitoring()
        self.root.quit()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = AutoAcceptGUI()
    gui.run()
