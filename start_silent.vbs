Option Explicit

Dim objShell, objFSO, strScriptDir, strBatFile
Dim intReturn

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

strScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
strBatFile = strScriptDir & "\start.bat"

If Not objFSO.FileExists(strBatFile) Then
    MsgBox "Error: start.bat not found" & vbCrLf & vbCrLf & _
           "Path: " & strBatFile, vbCritical, "ComfyUI Server"
    WScript.Quit 1
End If

MsgBox "ComfyUI Server is starting..." & vbCrLf & vbCrLf & _
       "The service will run in background.", vbInformation, "ComfyUI Server"

intReturn = objShell.Run("""" & strBatFile & """", 0, False)

Set objFSO = Nothing
Set objShell = Nothing

WScript.Quit 0
