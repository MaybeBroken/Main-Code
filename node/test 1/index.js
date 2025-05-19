if (process.versions.electron === undefined) {
    console.error("This script must be run with Electron, not Node.js. run 'npm run start' instead.");
    process.exit(1);
}

console.log("Init main window")
const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');
const { screen } = require('electron');
app.on('ready', () => {
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;

    const mainWindow = new BrowserWindow({
        width,
        height,
        x: 0,
        y: 0,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js')
        }
    });

    mainWindow.loadFile('index.html');
    mainWindow.setMenuBarVisibility(false);
    mainWindow.maximize();
});
app.on('window-all-closed', () => {
    console.log("All windows closed");
    app.quit();
});