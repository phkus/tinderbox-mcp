on linkFromNoteToNote(typeName, fromNote, toNote)
	tell application id "Cere"
		try
			set strType to typeName
			set strID to value of (attribute "ID" of toNote)
			delay 0.2
			evaluate fromNote with "linkTo(" & strID & "," & strType & ")"
		on error errMsg
			return "Link creation error: " & errMsg
		end try
	end tell
end linkFromNoteToNote

on run argv
	tell application id "Cere"
		try
			
			set sourcePath to ""
			set destinationPath to ""
			set theLinkType to ""
			set theDocument to ""
			
			-- Loop through each argument to find name-value pairs
			repeat with i from 1 to count of argv
				set currentArg to item i of argv
				
				-- Check if the argument is in the format "name=value"
				if currentArg contains "=" then
					-- Find the position of the first equals sign
					set equalPos to offset of "=" in currentArg
					
					-- Split at only the first equals sign
					set argName to text 1 thru (equalPos - 1) of currentArg
					set argValue to text (equalPos + 1) thru (length of currentArg) of currentArg
					
					-- Assign the value to the appropriate variable
					if argName is "source" then
						set sourcePath to argValue
					else if argName is "destination" then
						set destinationPath to argValue
					else if argName is "linktype" then
						set theLinkType to argValue
					else if argName is "document" then
						set theDocument to argValue
					end if
				end if
			end repeat
			
			if sourcePath is "" then
				display dialog "no source"
				return
			end if
			
			if destinationPath is "" then
				display dialog "no destination"
				return
			end if
			
			if theDocument is "" then
				set theDocument to name of front document
			end if
			
			tell document theDocument
				set sourceNote to (find note in it with path sourcePath)
				set destinationNote to (find note in it with path destinationPath)
				my linkFromNoteToNote(theLinkType, sourceNote, destinationNote)
			end tell
			
		on error errMsg
			return "Error: " & errMsg
		end try
	end tell
end run