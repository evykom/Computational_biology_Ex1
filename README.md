# Cellular automaton: spatial ecology and Kill-the-Winner dynamics

Computational biology coursework (**Bar-Ilan University**): a two-strain bacterial competition model on a toroidal grid with density-dependent “phage” activation on the fast strain.

## Table of contents

- [Theory](#theory)
- [Technical overview (how the code is organized)](#technical-overview-how-the-code-is-organized)
- [Running the pre-built program (no Python install)](#running-the-pre-built-program-no-python-install)
- [Building from source](#building-from-source)


---

## Theory

In microbial communities, fast-growing strains are expected to outcompete slower ones for limited space. Observations often show **coexistence** instead. **Kill-the-Winner** is one explanation: a virus (or predator) preferentially affects the **dominant** strain—when it becomes locally dense, it is more likely to suffer lysis, opening gaps that slower strains can use.

This project implements that idea as a **synchronous cellular automaton**:

| State        | Meaning |
|-------------|---------|
| **Empty**   | No bacterium. |
| **Strain A**| Fast reproducer carrying a dormant prophage; at high local density of healthy A neighbors, the phage activates. |
| **Strain B**| Slower reproducer; no phage. |
| **Inhibited** | Activated phage in an A cell: it does not reproduce; after **one** generation the cell dies and becomes empty. |

The grid uses **periodic (toroidal) boundaries**, **Moore neighborhoods** (8 neighbors), and parameters **P_A**, **P_B** (reproduction attempt probabilities) and **K** (minimum healthy-A neighbors to trigger activation). Setting **K = 9** effectively **disables** phage (only 8 neighbors exist), which is useful for the “fast strain wins without virus” baseline.

---

## Technical overview (how the code is organized)

| Path | Role |
|------|------|
| [`ex1_ca/cellular_automaton.py`](ex1_ca/cellular_automaton.py) | Cell state constants, toroidal neighbors, `random_init`, synchronous `step` (inhibited → empty, phage rule, reproduction with conflict resolution when two parents target the same empty cell). |
| [`ex1_ca/simulation.py`](ex1_ca/simulation.py) | `run_simulation` for batch runs; `count_cells` for population totals. |
| [`ex1_ca/cli.py`](ex1_ca/cli.py) | Command-line interface (`argparse`): batch mode, CSV export, `--gui`. |
| [`ex1_ca/gui.py`](ex1_ca/gui.py) | Optional GUI: tkinter controls + matplotlib view (e.g. A red, B blue, inhibited black). |
| [`main.py`](main.py) | Entry point used by PyInstaller. |
| [`ca_ex1.spec`](ca_ex1.spec) | PyInstaller spec (onedir bundle under `dist/ca_ex1/`). |
| [`build_exe.ps1`](build_exe.ps1) | Rebuild script: `pyinstaller --clean -y ca_ex1.spec`. |

The **Windows executable** in this repo is built with **PyInstaller** on Windows. It bundles Python, NumPy/Matplotlib, and Tcl/Tk for the GUI. It is **not** a cross-platform binary; running on macOS/Linux requires Python + dependencies from source (see below).

---

## Running the pre-built program (no Python install)

**Windows, 64-bit.** No Python needed. Keep the whole **`dist/ca_ex1`** folder (do not move only `ca_ex1.exe` out of it).

In **PowerShell** :

```powershell
git clone https://github.com/evykom/Computational_biology_Ex1.git
cd Computational_biology_Ex1\dist\ca_ex1
.\ca_ex1.exe
```

**Batch mode** (terminal only, no GUI): pass at least one flag, e.g. `.\ca_ex1.exe --generations 500 --seed 1` or `.\ca_ex1.exe --output run.csv`.

If a **DLL / VC++** error appears, install the [VC++ Redistributable (x64)](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist).

---

## Building from source 

From the project root (with Python 3.10+):

```powershell
pip install -r requirements.txt
```

Run without packaging (double-click / no args opens the GUI like the exe):

```powershell
python main.py
python main.py --generations 500 --seed 1
```

Build the Windows bundle:

```powershell
.\build_exe.ps1
```

Output: **`dist/ca_ex1/`** containing **`ca_ex1.exe`**.

---


