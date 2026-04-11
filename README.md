# FluidLearn 🌊

Advanced deep learning framework for computational fluid dynamics (CFD) data processing, training, and visualization.

## Quick Start

### Prerequisites

1. **Create conda environment**:
    `bash
    conda create -n torch python=3.13.12
    `

2. **Install CUDA and dependencies**:
    `bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
    pip install -r requirements.txt
    `

### Running the CLI

Once you have set up your environment and installed dependencies:

`bash
python init.py
`

Run this command from the project root directory. The CLI will launch an interactive menu.

---

## FluidLearn CLI Tool 🚀

Interactive command-line interface for FluidLearn workflows using **InquirerPy** for beautiful, responsive menus.

### Menu Structure

`
🚀 FluidLearn CLI - Main Menu:
  ├── Data Processing (placeholder - coming soon)
  ├── Training (placeholder - coming soon)
  ├── Visualization
  │   ├── Raw → Executes src/visualization.py
  │   └── Processed → Executes src/visualize.py
  └── Exit
`

### Features

- 🎨 **Beautiful interactive menus** using InquirerPy for an elegant UX
- 🔄 **Menu loops** - always return to main menu after execution
- ❌ **Error handling** - gracefully catches errors and returns to menu
- 🐍 **Function-based execution** - direct Python imports, no subprocesses
- ⌨️ **Keyboard navigation** - arrow keys to navigate, Enter to select

### Module Structure

- src/cli.py - Main CLI module with InquirerPy-driven menus
- src/visualization.py - Raw visualization (stub, ready for customization)
- src/visualize.py - Processed visualization (advanced 3D visualization)

### Usage Examples

**Basic workflow:**
1. Run python init.py from project root
2. Select "Visualization" from main menu
3. Choose "Raw" or "Processed" option
4. View visualization output
5. Menu returns automatically for next action

### Important Notes

- All execution is function-based (direct Python imports)
- Error messages are caught and displayed with emoji feedback
- Press Ctrl+C to exit from any menu at any time
- The CLI doesn't require additional installation - just run from project directory

---

## Project Structure

`
FluidLearn/
├── src/                    # Source code
│   ├── cli.py             # Main CLI module with InquirerPy
│   ├── visualization.py    # Raw visualization stub
│   └── visualize.py        # Processed visualization
├── data/                   # Data directory
│   ├── 00_cases/          # User-driven OpenFOAM case execution
│   ├── 01_raw/            # Framework-processed datasets
├── models/                # Trained models
├── notebooks/             # Jupyter notebooks
├── tests/                 # Test suite
├── pyproject.toml         # Project metadata
├── requirements.txt       # Project dependencies
├── init.py                # CLI entry point
└── README.md              # This file
`

## Data Format

The framework processes HDF5 files with the following structure:
- U - Velocity tensor
- p - Pressure tensor
- 	 - Time vector

Raw datasets are stored under data/01_raw/<dataset>/ with:
- mesh.h5 - Mesh information
- constants.json - Metadata
- <case_index>.h5 - Per-case data

## Development

### Running Tests

`bash
pytest tests/
`

### Building/Linting

Build and test commands are user-driven - refer to individual module documentation.

## Case Execution

OpenFOAM cases are executed manually in data/00_cases/. Refer to data/00_cases/README.md for detailed instructions on:
- Environment setup
- Mesh validation
- Simulation execution
- Output generation

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
