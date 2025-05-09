# Define the installer name and output
OutFile "OP Media Player Installer.exe"

# Request user-level privileges (no admin required)
RequestExecutionLevel user

# Define the installation directory in the user's local application data folder
InstallDir "$LOCALAPPDATA\OP Media Player"

# Define the section for installation
Section "Install"

    # Create the installation directory
    CreateDirectory "$INSTDIR"

    # Copy the Python script to the installation directory
    SetOutPath "$INSTDIR"
    File "OP Media Player.exe"
    File "Main.py"
    File "__YOUTUBEDOWNLOADER.py"
    File /r "src"
    File /r "po-token-generator"

    # Create a shortcut in the Windows Start Menu
    CreateShortCut "$SMPROGRAMS\OP Media Player.lnk" "$INSTDIR\OP Media Player.exe"

    # Wait for the executed program to finish before exiting
    Exec '"$INSTDIR\OP Media Player.exe"'

    # Exit the installer
    Quit
SectionEnd
