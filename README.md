# Cellular automaton: spatial ecology and Kill-the-Winner dynamics

Computational biology coursework (**Bar-Ilan University**): a two-strain bacterial competition model on a toroidal grid with density-dependent “phage” activation on the fast strain.

## Table of contents

- [Theory](#theory)
- [Technical overview (how the code is organized)](#technical-overview-how-the-code-is-organized)
- [Running the pre-built program (no Python install)](#running-the-pre-built-program-no-python-install)
- [Building from source (developers)](#building-from-source-developers)
- [Git: suggested command order (you run these locally)](#git-suggested-command-order-you-run-these-locally)
- [More detail for running and building](#more-detail-for-running-and-building)
- [License](#license)

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

If the repository includes **`dist/ca_ex1/`** (the full folder produced by PyInstaller):

1. **Download or clone** the repository.
2. Open **`dist/ca_ex1/`**. Do **not** move only `ca_ex1.exe` elsewhere—the **entire folder** (DLLs, `_internal`, etc.) must stay together.
3. Double-click **`ca_ex1.exe`**, or from PowerShell in that folder:

   ```powershell
   .\ca_ex1.exe
   .\ca_ex1.exe --gui
   .\ca_ex1.exe --k 9 --p-a 0.4 --p-b 0.08 --generations 500 --seed 1
   ```

**Requirements on the user’s PC:** Windows (same architecture you built for, typically 64-bit). **No** Python or `pip install` is needed. If Windows reports a missing **VC++** / DLL error, installing the latest [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) for x64 often fixes it.

**If `dist/` is not in the repo** (e.g. to keep the clone small), use a **GitHub Release** zip of `ca_ex1` and the same instructions after extracting.

---

## Building from source (developers)

From the project root (with Python 3.10+):

```powershell
pip install -r requirements.txt
```

Run without packaging:

```powershell
python main.py --p-a 0.35 --p-b 0.12 --k 4 --generations 500 --seed 123
python main.py --gui
```

Build the Windows bundle:

```powershell
.\build_exe.ps1
```

Output: **`dist/ca_ex1/`** containing **`ca_ex1.exe`**.

---

## Git: suggested command order (you run these locally)

Run in PowerShell from this project directory after `.gitignore` and `README.md` exist and optional rebuild of `dist\ca_ex1\`.

1. `git init`
2. `git branch -M main`
3. `git status`
4. `git add .`
5. `git commit -m "Initial commit: CA Exercise 1 source and Windows bundle"`

On GitHub, create an **empty** repository (no README if you already committed one). Then:

6. `git remote add origin https://github.com/<YOUR_USER>/<REPO_NAME>.git`
7. `git push -u origin main`

Alternatively, with [GitHub CLI](https://cli.github.com/): `gh auth login` then `gh repo create <REPO_NAME> --public --source=. --remote=origin --push`.

---

## More detail for running and building

See [`README_RUN.txt`](README_RUN.txt) for a first-person build/run log and flag reference.

---

## License

No license is set by default. Add a `LICENSE` file (e.g. MIT) if you want to clarify reuse rights.
