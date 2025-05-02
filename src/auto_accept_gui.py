import tkinter as tk
from tkinter import ttk
import threading
import time
import logging
import sys
import os
from pathlib import Path
import pyautogui
from PIL import Image, ImageTk

from lol_auto_accept import LoLAutoAccept
from controller import Controller
from config_utils import load_config, save_config

class AutoAcceptGUI:
    def __init__(self, controller=None):
        self.root = tk.Tk()
        self.root.title("LoL Auto Accept")
        self.root.geometry("250x220")
        self.root.resizable(False, False)  # ウィンドウサイズを固定
        
        # 黒ベースの洗練されたテーマを適用
        self.configure_dark_theme()
        
        try:
            # Use provided controller or create a new one
            if controller is None:
                self.auto_accept = LoLAutoAccept()
                self.controller = Controller(self.auto_accept, self)
            else:
                self.controller = controller
                self.auto_accept = controller.auto_accept
            
            # Set window icon to match tray icon
            if getattr(sys, 'frozen', False):
                base_dir = sys._MEIPASS
            else:
                base_dir = str(Path(__file__).resolve().parent.parent)
                
            # Try to use the ICO file for the taskbar icon
            icon_path = os.path.join(base_dir, 'resources', 'tray_icon.ico')
            
            # If ICO file doesn't exist, use the PNG as fallback
            if not os.path.exists(icon_path):
                icon_path = os.path.join(base_dir, 'resources', 'tray_icon.png')
                logging.info(f"ICOファイルが見つからないため、PNGファイルを使用します: {icon_path}")
                
            # Check if icon exists
            if not os.path.exists(icon_path):
                logging.warning(f"ウィンドウアイコンが見つかりません: {icon_path}")
                # Try to find any icon in resources
                resources_dir = os.path.join(base_dir, 'resources')
                if os.path.exists(resources_dir):
                    for file in os.listdir(resources_dir):
                        if file.endswith('.ico') or file.endswith('.png'):
                            icon_path = os.path.join(resources_dir, file)
                            logging.info(f"代替アイコンを使用します: {icon_path}")
                            break
            
            # Set window icon if icon exists
            if os.path.exists(icon_path):
                if icon_path.endswith('.ico'):
                    # For Windows taskbar icon, use iconbitmap with ICO file
                    self.root.iconbitmap(icon_path)
                    logging.info(f"ウィンドウアイコン(ICO)を設定しました: {icon_path}")
                else:
                    # Fallback to iconphoto with PNG for non-ICO files
                    icon_image = Image.open(icon_path)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    self.root.iconphoto(True, icon_photo)
                    logging.info(f"ウィンドウアイコン(PNG)を設定しました: {icon_path}")
        except Exception as e:
            logging.error(f"ウィンドウアイコン設定中にエラーが発生しました: {str(e)}")
        
        # メインフレーム
        self.app_frame = tk.Frame(self.root, bg="#1E1E1E", padx=5, pady=5)
        self.app_frame.pack(fill=tk.BOTH, expand=True)
        
        # ボタンフレーム
        button_frame = tk.Frame(self.app_frame, bg="#1E1E1E")
        button_frame.pack(fill=tk.X, pady=(5, 10))
        
        # ボタン
        self.start_button = tk.Button(button_frame, text="開始", command=self.start_monitoring, 
                                     bg="#252525", fg="#E0E0E0", activebackground="#3A3A3A", 
                                     activeforeground="#FFFFFF", relief=tk.RAISED, bd=1)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)
        
        self.stop_button = tk.Button(button_frame, text="停止", command=self.stop_monitoring, 
                                    bg="#252525", fg="#E0E0E0", activebackground="#3A3A3A", 
                                    activeforeground="#FFFFFF", relief=tk.RAISED, bd=1,
                                    state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, padx=(5, 0), expand=True, fill=tk.X)

        # チェックボックスフレーム
        checkbox_frame = tk.Frame(self.app_frame, bg="#1E1E1E")
        checkbox_frame.pack(fill=tk.X, pady=5)
        
        # 自動停止チェックボックス
        self.auto_stop_var = tk.BooleanVar(value=True)
        self.auto_stop_checkbox = tk.Checkbutton(checkbox_frame, text="自動で停止する", variable=self.auto_stop_var,
                                              bg="#1E1E1E", fg="#E0E0E0", selectcolor="#252525",
                                              activebackground="#1E1E1E", activeforeground="#FFFFFF")
        self.auto_stop_checkbox.pack(anchor=tk.W, pady=(0, 5))
        
        # 自動開始チェックボックス
        self.auto_start_var = tk.BooleanVar(value=True)  # デフォルトでオン
        self.auto_start_checkbox = tk.Checkbutton(checkbox_frame, text="マッチング時に自動開始", variable=self.auto_start_var,
                                               bg="#1E1E1E", fg="#E0E0E0", selectcolor="#252525",
                                               activebackground="#1E1E1E", activeforeground="#FFFFFF")
        self.auto_start_checkbox.pack(anchor=tk.W, pady=(0, 5))
        
        # 終了ボタンフレーム
        exit_frame = tk.Frame(self.app_frame, bg="#1E1E1E")
        exit_frame.pack(fill=tk.X, pady=5)
        
        self.exit_button = tk.Button(exit_frame, text="終了", command=self.exit_application,
                                   bg="#252525", fg="#E0E0E0", activebackground="#3A3A3A",
                                   activeforeground="#FFFFFF", relief=tk.RAISED, bd=1)
        self.exit_button.pack(fill=tk.X)
        
        # ステータスラベル
        self.status_label = tk.Label(self.app_frame, text="待機中", bg="#1E1E1E", fg="#E0E0E0")
        self.status_label.pack(fill=tk.X, pady=(10, 0))
        
        try:
            # Configure window close event to hide instead of quit
            self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
            
            # Start auto detection
            self.start_auto_detection()
        except Exception as e:
            logging.error(f"GUIの初期化中にエラーが発生しました: {str(e)}")
            self.root.destroy()
            sys.exit(1)

    def configure_dark_theme(self):
        """黒ベースの洗練されたテーマを設定"""
        # ルートウィンドウの背景色を設定
        self.root.configure(bg="#1E1E1E")
        
        # システム全体の設定
        self.root.option_add("*Background", "#1E1E1E")
        self.root.option_add("*Foreground", "#E0E0E0")
        
        # メインのアプリフレーム
        self.app_frame = tk.Frame(self.root, bg="#1E1E1E", padx=5, pady=5)
        self.app_frame.pack(fill=tk.BOTH, expand=True)

    def start_move(self, event):
        """Window drag operation - start"""
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        """Window drag operation - stop"""
        self.x = None
        self.y = None

    def do_move(self, event):
        """Window drag operation - move"""
        if self.x is not None and self.y is not None:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")
        
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
        self.status_label.config(text="監視中...", fg="#00FF00")  # 緑色のテキスト

    def stop_monitoring(self):
        self.controller.stop()
        
    def update_ui_on_stop(self, message="停止中"):
        """Called by controller when monitoring stops"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text=message, fg="#E0E0E0")  # 通常の文字色に戻す

    def exit_application(self):
        self.controller.exit()

    def hide_window(self):
        """最小化してタスクバーに残す"""
        self.root.iconify()
        
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
        self.status_label.config(text="設定をリロードしました", fg="#00AAFF")  # 青色のテキスト

    def save_settings(self):
        save_config(self.auto_accept.config)
        self.status_label.config(text="設定を保存しました", fg="#00AAFF")  # 青色のテキスト

    def run(self):
        self.root.mainloop()
