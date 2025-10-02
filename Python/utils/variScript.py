import os

mode = input("mode (1=app, 2=script): ")
while True:
    if mode == "1":
        try:
            appName = input("\napp directory (ex. /folder/name.app):\n| -> ")
            os.system(f'chmod +x "{appName}/Contents/MacOs/{appName}"')
            os.system(
                f'xattr -d com.apple.quarantine "{appName}/Contents/MacOs/{appName}"'
            )
            print("finished")
        except:
            print("\nerr\n")
    elif mode == "2":
        try:
            scriptName = input("\nscript path (ex. /folder/name.py): \n | -> ")
            if (scriptName.startswith('"') and scriptName.endswith('"')) or (
                scriptName.startswith("'") and scriptName.endswith("'")
            ):
                scriptName = scriptName[1:-1]
            os.system(f'chmod +x "{scriptName}"')
            os.system(f'xattr -d com.apple.quarantine "{scriptName}"')
            print("finished")
        except:
            print("\nerr\n")
    else:
        print("\nerr\n")
    mode = input("mode (1=app, 2=script):")
