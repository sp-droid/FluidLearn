# Standard
import logging
from pathlib import Path

# Third-party
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

# Local
import fluidlearn as fl

# Set up logging
handler = logging.StreamHandler()
formatter = logging.Formatter('%(name)s: %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger("fluidlearn")
logger.addHandler(handler)
logger.setLevel(logging.WARNING)

def get_version():
    """Extract version from main package"""
    from . import __version__
    return __version__

def print_banner():
    """Print fancy ASCII banner with version"""
    version = get_version()
    banner = f"""
    ╔════════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                    ║
    ║   ███████╗██╗     ██╗   ██╗██╗██████╗ ██╗     ███████╗ █████╗ ██████╗ ███╗   ██╗   ║
    ║   ██╔════╝██║     ██║   ██║██║██╔══██╗██║     ██╔════╝██╔══██╗██╔══██╗████╗  ██║   ║
    ║   █████╗  ██║     ██║   ██║██║██║  ██║██║     █████╗  ███████║██████╔╝██╔██╗ ██║   ║
    ║   ██╔══╝  ██║     ██║   ██║██║██║  ██║██║     ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║   ║
    ║   ██║     ███████╗╚██████╔╝██║██████╔╝███████╗███████╗██║  ██║██║  ██║██║ ╚████║   ║
    ║   ╚═╝     ╚══════╝ ╚═════╝ ╚═╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ║
    ║                                                                                    ║
    ╚════════════════════════════════════════════════════════════════════════════════════╝
    FluidLearn v{version} - Advanced CFD Deep Learning Framework
    """
    print(banner)

def raw_data_submenu():
    """Submenu for data options."""
    while True:
        choice = inquirer.select(
            message="\n🎨 Raw Data Options:",
            choices=[
                Choice(value="raw", name="🎨 Visualise"),
                Choice(value="back", name="🔙 Back to Main Menu"),
                Choice(value="exit", name="🚪 Exit"),
            ],
        ).execute()
        
        if choice == "raw":
            from fluidlearn.vis.Raw_visualization import gui_main
            gui_main()
            return True
        elif choice == "back":
            return False  # Go back, don't exit
        elif choice == "exit":
            return True  # Exit application

def data_submenu():
    """Submenu for data options."""
    while True:
        choice = inquirer.select(
            message="\n🎨 Data Options:",
            choices=[
                Choice(value="raw", name="📊 Raw Data"),
                Choice(value="back", name="🔙 Back to Main Menu"),
                Choice(value="exit", name="🚪 Exit"),
            ],
        ).execute()
        
        if choice == "raw":
            if raw_data_submenu():  # If True, exit
                return True
        elif choice == "back":
            return False
        elif choice == "exit":
            return True


def main_menu():
    print_banner()
    """Main menu loop."""
    while True:
        choice = inquirer.select(
            message="\n🚀 FluidLearn - Main Menu:",
            choices=[
                Choice(value="data", name="📊 Data"),
                Choice(value="train", name="🎓 Training"),
                Choice(value="debug_mode", name="🐞 Switch Debug Mode"),
                Choice(value="exit", name="🚪 Exit"),
            ],
        ).execute()
        
        if choice == "data":
            if data_submenu():  # If True, exit
                break
        elif choice == "train":
            pass
            # training()
        elif choice == "debug_mode":
            if logger.getEffectiveLevel() == logging.WARNING:
                logger.setLevel(level=logging.DEBUG)
                print("\n🐞 Logging level set to DEBUG.\n")
                logger.debug("This is a debug message.")
                logger.warning("This is a warning message.")
            else:
                logger.setLevel(level=logging.WARNING)
                print("\n🐞 Logging level set to WARNING.\n")
        elif choice == "exit":
            break
    
    print("\n👋 Thank you for using FluidLearn!\n")