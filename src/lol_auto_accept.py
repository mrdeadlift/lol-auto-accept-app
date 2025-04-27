import pyautogui
import cv2
import time
import logging
import sys
import os
from pathlib import Path

from config_utils import load_config

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
