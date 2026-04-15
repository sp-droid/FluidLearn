"""
FluidLearn Interactive CLI Tool

Uses InquirerPy for beautiful, interactive menu navigation.
"""

from pathlib import Path
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

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


def data_processing():
    """Handle data processing workflow."""
    print("\n🔄 Data Processing selected")
    print("   This feature is coming soon! Stay tuned.\n")


def training():
    """Handle training workflow."""
    print("\n🎓 Training selected")
    print("   This feature is coming soon! Stay tuned.\n")


def visualization_raw():
    """Execute raw visualization from src/visualization.py"""
    print("\n📊 Executing raw visualization...")
    import sys
    src_path = Path(__file__).parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    import visualization
    print("✅ Raw visualization completed!\n")


def visualization_processed():
    """Execute processed visualization from src/visualize.py"""
    print("\n📈 Executing processed visualization...")
    import sys
    src_path = Path(__file__).parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    import visualize
    print("✅ Processed visualization completed!\n")


def visualization_submenu():
    """Submenu for visualization options."""
    while True:
        choice = inquirer.select(
            message="🎨 Visualization Options:",
            choices=[
                Choice(value="raw", name="📊 Raw Visualization"),
                Choice(value="processed", name="📈 Processed Visualization"),
                Choice(value="back", name="🔙 Back to Main Menu"),
            ],
        ).execute()
        
        if choice == "raw":
            visualization_raw()
        elif choice == "processed":
            visualization_processed()
        elif choice == "back":
            break


def main_menu():
    print_banner()

    """Main menu loop."""
    while True:
        choice = inquirer.select(
            message="🚀 FluidLearn - Main Menu:",
            choices=[
                Choice(value="data", name="📊 Data Processing"),
                Choice(value="train", name="🎓 Training"),
                Choice(value="viz", name="🎨 Visualization"),
                Choice(value="exit", name="🚪 Exit"),
            ],
        ).execute()
        
        if choice == "data":
            data_processing()
        elif choice == "train":
            training()
        elif choice == "viz":
            visualization_submenu()
        elif choice == "exit":
            print("\n👋 Thank you for using FluidLearn!\n")
            break