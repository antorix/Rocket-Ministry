Option Explicit

Dim baseFolder, linkFile, targetPath, objShell, strPath

   Set objShell = Wscript.CreateObject("Wscript.Shell")
   strPath = objShell.SpecialFolders("Desktop")
 

    With WScript.CreateObject("Scripting.FileSystemObject")
        baseFolder = .BuildPath( .GetParentFolderName( WScript.ScriptFullName ), "\")
        linkFile   = .BuildPath( strPath, "Rocket Ministry.lnk" )
	targetPath = .BuildPath( baseFolder, "Rocket Ministry.pyw" )
    End With 

    With WScript.CreateObject("WScript.Shell").CreateShortcut( linkFile )

        .TargetPath = targetPath
        .WorkingDirectory = baseFolder
		.IconLocation= baseFolder & "icon.ico"
        .Save
    End With