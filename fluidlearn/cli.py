"""
FluidLearn Interactive CLI Tool

Uses InquirerPy for beautiful, interactive menu navigation.
"""
# Standard
from pathlib import Path

# Third-party
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

# Local
import fluidlearn as fl

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

# def visualization_raw():
#     """Execute raw visualization from src/visualization.py"""
#     print("\n📊 Executing raw visualization...")
#     import sys
#     src_path = Path(__file__).parent
#     if str(src_path) not in sys.path:
#         sys.path.insert(0, str(src_path))
    
#     import visualization
#     print("✅ Raw visualization completed!\n")

def raw_data_submenu():
    """Submenu for data options."""
    while True:
        choice = inquirer.select(
            message="🎨 Raw Data Options:",
            choices=[
                Choice(value="raw", name="🎨 Visualise"),
                Choice(value="back", name="🔙 Back to Main Menu"),
            ],
        ).execute()
        
        if choice == "raw":
            from fluidlearn.vis.GUIunstructured import gui_main
            gui_main()
        elif choice == "back":
            break

def data_submenu():
    """Submenu for data options."""
    while True:
        choice = inquirer.select(
            message="🎨 Data Options:",
            choices=[
                Choice(value="raw", name="📊 Raw Data"),
                Choice(value="back", name="🔙 Back to Main Menu"),
            ],
        ).execute()
        
        if choice == "raw":
            raw_data_submenu()
        elif choice == "back":
            break


def main_menu():
    print_banner()

    """Main menu loop."""
    while True:
        choice = inquirer.select(
            message="🚀 FluidLearn - Main Menu:",
            choices=[
                Choice(value="data", name="📊 Data"),
                Choice(value="train", name="🎓 Training"),
                Choice(value="exit", name="🚪 Exit"),
            ],
        ).execute()
        
        if choice == "data":
            data_submenu()
        elif choice == "train":
            pass
            # training()
        elif choice == "exit":
            print("\n👋 Thank you for using FluidLearn!\n")
            break