"""
FluidLearn Interactive CLI Tool

Uses InquirerPy for beautiful, interactive menu navigation.
"""

from pathlib import Path
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import re


def get_version():
    """Extract version from pyproject.toml"""
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path) as file:
            content = file.read()
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    except Exception:
        pass
    return "0.1.0"


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
    try:
        import sys
        src_path = Path(__file__).parent
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        try:
            import visualization
            print("✅ Raw visualization completed!\n")
        except ModuleNotFoundError:
            print("⚠️  src/visualization.py not found. Please create this module first.\n")
    except Exception as e:
        print(f"❌ Error during raw visualization: {str(e)}\n")


def visualization_processed():
    """Execute processed visualization from src/visualize.py"""
    print("\n📈 Executing processed visualization...")
    try:
        import sys
        src_path = Path(__file__).parent
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        try:
            import visualize
            print("✅ Processed visualization completed!\n")
        except ModuleNotFoundError:
            print("⚠️  src/visualize.py not found.\n")
    except Exception as e:
        print(f"❌ Error during processed visualization: {str(e)}\n")


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


def cli():
    """Entry point for the CLI."""
    print_banner()
    main_menu()


if __name__ == "__main__":
    cli()
