# PDF EDITOR

<img width="1365" height="693" alt="Captura de pantalla 2025-11-21 111030" src="https://github.com/user-attachments/assets/539af4f5-ee6b-4ddc-88b7-8ef944338d5c" />

### run windows
 ```
   run.bat
 ```
### linux
 ```
   sh run.sh
 ```




# Building Standalone Executables

This document explains how to build standalone executables for the PDF Visual Editor on both Windows and Linux.

## Quick Start

### Windows

1. Open a terminal in the project directory
2. Run the build script:
   ```
   build_exe.bat
   ```
3. Find the executable in `dist\PDF Visual Editor.exe`

### Linux

1. Open a terminal in the project directory
2. Make the script executable (first time only):
   ```bash
   chmod +x build_exe.sh
   ```
3. Run the build script:
   ```bash
   ./build_exe.sh
   ```
4. Find the executable in `dist/PDF Visual Editor`

## Requirements

### Common (All Platforms)
- Python 3.8 or higher
- All dependencies from `requirements.txt` installed
- ~500MB free disk space for build artifacts

### Windows Specific
- Windows 7 or later (64-bit)

### Linux Specific
- Modern Linux distribution (Ubuntu 20.04+, Fedora 35+, etc.)
- System packages required:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-dev libxcb-xinerama0 libxcb-cursor0
  
  # Fedora/RHEL
  sudo dnf install python3-devel libxcb
  ```

## Build Process

### Windows (`build_exe.bat`)
The build script will:
1. Activate your virtual environment (if available)
2. Install/update PyInstaller
3. Run PyInstaller with the spec file
4. Create a single-file `.exe` with all dependencies bundled
5. Display file size and location

### Linux (`build_exe.sh`)
The build script will:
1. Activate your virtual environment (if available)
2. Install/update PyInstaller
3. Run PyInstaller with the spec file
4. Create a single-file binary with all dependencies bundled
5. Make the binary executable (`chmod +x`)
6. Display file size and location

## Output

### Windows
After a successful build, you'll find:
- `dist\PDF Visual Editor.exe` - The standalone executable (~100-120MB)
- `build\` - Temporary build files (can be deleted)

### Linux
After a successful build, you'll find:
- `dist/PDF Visual Editor` - The standalone binary (~100-120MB)
- `build/` - Temporary build files (can be deleted)

## Distribution

### Windows
The `PDF Visual Editor.exe` file is completely standalone:
- No Python installation required
- No dependency installation needed
- Can be copied to any Windows PC (64-bit, Windows 7+)
- First launch may take 10-15 seconds (extracting to temp folder)
- No installation required - just double-click to run

### Linux
The `PDF Visual Editor` binary is completely standalone:
- No Python installation required
- No dependency installation needed
- Can be copied to any Linux system with compatible glibc (most modern distros)
- First launch may take 10-15 seconds (extracting to temp folder)
- Run from terminal: `./PDF\ Visual\ Editor` or double-click in file manager
- **Note**: Built on the same Linux distro/version as target systems for best compatibility
  - Binary built on Ubuntu 22.04 works on Ubuntu 22.04+ and similar distros
  - For maximum compatibility, build on the oldest supported distro version

## Troubleshooting

### Build Fails with "Module not found"
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Add missing modules to `hiddenimports` in `pdf_visual_editor.spec`

### Antivirus Blocks the Build
- PyInstaller executables sometimes trigger false positives
- Add an exception for the `dist` folder in your antivirus
- Build on a clean system and scan the result

### Executable Crashes on Launch
- Test dependencies: `python main.py` should work first
- Check the spec file includes all resource files
- Run with console enabled to see error messages:
  - In `pdf_visual_editor.spec`, set `console=True`
  - Rebuild and check console output

### Resources Not Loading (Themes/Logos Missing)
- Verify theme files exist in `themes/` folder
- Verify logo files exist in `resources/` folder
- Check the paths in `pdf_visual_editor.spec` match your structure

### File Size Too Large
- The executable includes PyQt6 and PDF libraries (~40-60MB base)
- Additional size comes from Python runtime and your code
- This is normal for PyQt6 applications
- Alternative: Use one-folder mode (faster, but multiple files)

### Linux: Missing System Libraries
If the binary fails to run with library errors:
```bash
# Check missing dependencies
ldd "dist/PDF Visual Editor"

# Install common Qt dependencies
# Ubuntu/Debian
sudo apt-get install libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11-0

# Fedora/RHEL
sudo dnf install libxcb xcb-util-cursor libxkbcommon-x11
```

### Linux: "Permission Denied" Error
Make the binary executable:
```bash
chmod +x "dist/PDF Visual Editor"
```

### Linux: Binary Won't Run on Different Distro
- PyInstaller binaries are tied to the glibc version of the build system
- Build on the oldest distro you want to support
- Alternative: Use AppImage or Flatpak for better cross-distro compatibility

## Advanced Configuration

### One-Folder Mode

To create a folder with .exe + supporting files instead of a single file:

1. Edit `pdf_visual_editor.spec`
2. Replace the `EXE` section with:
   ```python
   exe = EXE(
       pyz,
       a.scripts,
       [],
       exclude_binaries=True,
       name='PDF Visual Editor',
       debug=False,
       bootloader_ignore_signals=False,
       strip=False,
       upx=True,
       console=False,
   )
   
   coll = COLLECT(
       exe,
       a.binaries,
       a.zipfiles,
       a.datas,
       strip=False,
       upx=True,
       upx_exclude=[],
       name='PDF Visual Editor',
   )
   ```
3. Rebuild with `build_exe.bat`

### Adding an Icon

1. Create or obtain a `.ico` file
2. Place it in the project root (e.g., `app_icon.ico`)
3. Edit `pdf_visual_editor.spec` and add `icon='app_icon.ico'` to the `EXE` section
4. Rebuild

## Manual Build

### Windows
If you prefer not to use the batch script:

```powershell
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller pdf_visual_editor.spec --clean --noconfirm

# Find output in dist\
```

### Linux
If you prefer not to use the shell script:

```bash
# Install PyInstaller
pip install pyinstaller

# Build the binary
pyinstaller pdf_visual_editor.spec --clean --noconfirm

# Make executable
chmod +x "dist/PDF Visual Editor"

# Find output in dist/
```

## Cleaning Build Artifacts

To clean up temporary files:

```bash
rmdir /s /q build
rmdir /s /q dist
del *.spec.bak
```

## Version Information

To add version information to the .exe:

1. Create a `version_info.txt` file with Windows version resource format
2. Add `version='version_info.txt'` to the `EXE` section in the spec file
3. Rebuild





