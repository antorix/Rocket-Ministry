Set oShell = CreateObject ("Wscript.Shell") 
Dim strArgs

strArgs = "cmd /c create_shortcuts.vbs"
oShell.Run strArgs, 0, false

strArgs = "cmd /c main.py"
oShell.Run strArgs, 0, false