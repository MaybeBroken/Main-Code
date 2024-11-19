import os

while True:
    try:
        appName = input("\napp directory (ex. /folder/name.app): \n")
        os.system(f'chmod +x "{appName}/Contents/MacOs/{appName}"')
        os.system(f'xattr -d com.apple.quarantine "{appName}/Contents/MacOs/{appName}"')
        print("finished")
    except:
        print("\nerr\n")
