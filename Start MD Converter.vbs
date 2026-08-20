' Start MD Converter - Double-click to launch
' Runs the Flask server hidden (no console window) and opens the browser

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Get the directory this script lives in
scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)

' Build the path to the Python executable in the venv
pythonExe = scriptDir & "\.venv\Scripts\pythonw.exe"
appFile = scriptDir & "\app.py"

' Check if venv exists
If Not FSO.FileExists(pythonExe) Then
    MsgBox "Virtual environment not found!" & vbCrLf & vbCrLf & _
           "Please run setup first:" & vbCrLf & _
           "  1. Open a terminal in the project folder" & vbCrLf & _
           "  2. Run: python -m venv venv" & vbCrLf & _
           "  3. Run: venv\Scripts\pip install -r requirements.txt", _
           vbCritical, "MD Converter - Setup Required"
    WScript.Quit
End If

' Launch the app with pythonw.exe (no console window)
WshShell.CurrentDirectory = scriptDir
WshShell.Run """" & pythonExe & """ """ & appFile & """", 0, False

' Wait a moment for server to start, then open browser
WScript.Sleep 2000
WshShell.Run "http://localhost:5000", 1, False
