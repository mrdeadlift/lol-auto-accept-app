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

# ログの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

class LoLAutoAccept:
    def __init__(self):
        # pyautoguiの設定
        pyautogui.FAILSAFE = True  # 画面端にマウスを移動で停止
        self.button_image = 'accept_button.png'
        
        # ボタン画像が存在しない場合は終了
        if not os.path.exists(self.button_image):
            logging.error(f"ボタン画像 '{self.button_image}' が見つかりません。")
            logging.info("プログラムを終了します。")
            sys.exit(1)

    def scan_screen(self):
        """画面をスキャンしてマッチング画面の承認ボタンを探す"""
        try:
            # 画面上でボタン画像を探す
            button_pos = pyautogui.locateOnScreen(self.button_image, confidence=0.8)
            
            if button_pos is not None:
                # ボタンが見つかった場合、中央をクリック
                center = pyautogui.center(button_pos)
                pyautogui.click(center)
                logging.info("承認ボタンをクリックしました")
                # クリック後に少し待機
                time.sleep(2)
                return True
            return False
            
        except Exception as e:
            logging.error(f"エラーが発生しました: {str(e)}")
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
        self.root.geometry("300x150")
        
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ボタン
        self.start_button = ttk.Button(main_frame, text="開始", command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_button = ttk.Button(main_frame, text="停止", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)

        # 自動停止チェックボックス
        self.auto_stop_var = tk.BooleanVar()
        self.auto_stop_checkbox = ttk.Checkbutton(main_frame, text="自動で停止する", variable=self.auto_stop_var)
        self.auto_stop_checkbox.grid(row=1, column=0, columnspan=2, pady=5)
        
        self.exit_button = ttk.Button(main_frame, text="終了", command=self.exit_application)
        self.exit_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # ステータスラベル
        self.status_label = ttk.Label(main_frame, text="待機中")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        self.auto_accept = LoLAutoAccept()
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        self.monitoring = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="監視中...")
        
        def monitor():
            while self.monitoring:
                if self.auto_accept.scan_screen() and self.auto_stop_var.get():
                    self.stop_monitoring()
                    self.status_label.config(text="承認完了 - 停止中")
                    break
                time.sleep(1)
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="停止中")
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

    def exit_application(self):
        if self.monitoring:
            self.stop_monitoring()
        self.root.quit()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = AutoAcceptGUI()
    gui.run()
