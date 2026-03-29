# Rebuild the Windows bundle after changing code. Run from this folder in PowerShell:
#   .\build_exe.ps1
# Output: dist\ca_ex1\ca_ex1.exe (keep the entire ca_ex1 folder when submitting).

pyinstaller --clean -y ca_ex1.spec
