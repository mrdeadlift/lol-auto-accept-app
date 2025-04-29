import threading
import logging
import time
from pathlib import Path

class Controller:
    def __init__(self, auto_accept, gui=None):
        self.auto_accept = auto_accept
        self.gui = gui
        self.monitoring = False
        self.monitor_thread = None
        self.running = True
        self.tray_icon = None
    
    def start(self):
        """Start monitoring for accept button"""
        if self.monitoring:
            return
        
        self.monitoring = True
        if self.gui:
            self.gui.update_ui_on_start()
        # Update tray icon if available
        if self.tray_icon:
            self.tray_icon.update_menu_state(True)
        
        def monitor():
            logging.info("監視を開始しました")
            while self.monitoring and self.running:
                try:
                    is_accepted = self.auto_accept.scan_screen()
                    if is_accepted and self.gui and self.gui.auto_stop_var.get():
                        # Set monitoring to false first to avoid recursion
                        self.monitoring = False
                        if self.gui:
                            self.gui.update_ui_on_stop("承認完了 - 停止中")
                        # Update tray icon if available
                        if self.tray_icon:
                            self.tray_icon.update_menu_state(False)
                        break
                except Exception as e:
                    logging.error(f"監視中にエラーが発生しました: {str(e)}")
                time.sleep(1)
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
    
    def stop(self):
        """Stop monitoring for accept button"""
        if not self.monitoring:
            return
            
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        
        if self.gui:
            self.gui.update_ui_on_stop()
        # Update tray icon if available
        if self.tray_icon:
            self.tray_icon.update_menu_state(False)
    
    def show_window(self):
        """Show the GUI window if it exists"""
        if self.gui:
            self.gui.show()
    
    def exit(self):
        """Exit the application completely"""
        self.running = False
        self.stop()
        if self.gui:
            self.gui.quit()
        else:
            # If no GUI, we need to exit the application directly
            import sys
            sys.exit(0)
