import json
import logging
import sys
import argparse
from pathlib import Path

# Define DEFAULT_CONFIG
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
    except PermissionError as e:
        import logging as log_module
        log_module.error(f"設定ファイル保存失敗 (権限エラー): {e}")
    except IOError as e:
        import logging as log_module
        log_module.error(f"設定ファイル保存失敗 (IOエラー): {e}")
    except Exception as e:
        logging.error(f"設定ファイル保存失敗: {e}")

def parse_arguments():
    parser = argparse.ArgumentParser(description='LoL Auto Accept - マッチング画面の自動承認ツール')
    parser.add_argument('--nogui', action='store_true', help='GUIを表示せずにコマンドラインで実行')
    return parser.parse_args()
