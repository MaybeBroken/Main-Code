import os
while True:
    usrName = os.getlogin()
    appName = input("\nappname: \n")
    os.system(
        f'chmod +x "/Users/{usrName}/Downloads/{appName}.app/Contents/MacOs/{appName}"'
    )
    os.system(
        f'xattr -d com.apple.quarantine "/Users/{usrName}/Downloads/{appName}.app/Contents/MacOs/{appName}"'
    )
    print('finished')