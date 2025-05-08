import logging
import sys
import time

from .lol_auto_accept import LoLAutoAccept
from .auto_accept_gui import AutoAcceptGUI
from .controller import Controller
from .tray_icon import TrayIcon
from .config_utils import parse_arguments

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Create the auto accept instance
    auto_accept = LoLAutoAccept()
    
    if args.nogui:
        # Run in background mode without GUI
        controller = Controller(auto_accept)
        tray_icon = TrayIcon(controller)
        # Set tray_icon reference in controller
        controller.tray_icon = tray_icon
        tray_icon.run()
        
        # Start monitoring automatically in nogui mode
        controller.start()
        
        # Keep the main thread alive
        try:
            while controller.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("キーボード割り込みによりプログラムを終了します。")
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
        # Set tray_icon reference in controller
        controller.tray_icon = tray_icon
        tray_icon.run()
        
        # Run the GUI
        gui.run()
        
        # Clean up tray icon when GUI exits
        try:
            tray_icon.shutdown()
        except Exception as e:
            logging.error(f"終了時にエラーが発生しました: {str(e)}")
