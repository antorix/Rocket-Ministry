Option Explicit

Dim baseFolder, linkFile1, linkFile2, targetPath, objShell1, objShell2, desktopPath, progPath, oFSO
	
	Set objShell1 = Wscript.CreateObject("Wscript.Shell")
	desktopPath = objShell1.SpecialFolders("Desktop")
	
	' Создание папки на рабочем столе
	'Set oFSO = CreateObject("Scripting.FileSystemObject")	
	'oFSO.CreateFolder desktopPath & "\Rocket Ministry"	
   
	Set objShell2 = Wscript.CreateObject("Wscript.Shell")
	progPath = objShell2.SpecialFolders("Programs")
	 

    With WScript.CreateObject("Scripting.FileSystemObject")
        baseFolder = .BuildPath( .GetParentFolderName( WScript.ScriptFullName ), "\")
        linkFile1   = .BuildPath( desktopPath, "Rocket Ministry.lnk" )
		linkFile2   = .BuildPath( progPath, "Rocket Ministry.lnk" )
	targetPath = .BuildPath( baseFolder, "Rocket Ministry.vbs" )
    End With 

    With WScript.CreateObject("WScript.Shell").CreateShortcut( linkFile1 )

        .TargetPath = targetPath
        .WorkingDirectory = baseFolder
		.IconLocation= baseFolder & "icon.ico"
        .Save
    End With
	
	With WScript.CreateObject("WScript.Shell").CreateShortcut( linkFile2 )

        .TargetPath = targetPath
        .WorkingDirectory = baseFolder
		.IconLocation= baseFolder & "icon.ico"
        .Save
    End With
