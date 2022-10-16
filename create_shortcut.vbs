Option Explicit

Dim baseFolder, linkFile, targetPath

    With WScript.CreateObject("Scripting.FileSystemObject")
        baseFolder = .BuildPath( .GetParentFolderName( WScript.ScriptFullName ), "\")
        linkFile   = .BuildPath( baseFolder, "Rocket Ministry.lnk" )
        targetPath = .BuildPath( baseFolder, "Rocket Ministry.pyw" )
    End With 

    With WScript.CreateObject("WScript.Shell").CreateShortcut( linkFile )
        .TargetPath = targetPath
        .WorkingDirectory = baseFolder
		.IconLocation= "icon.ico"
        .Save
    End With 
	
	
	