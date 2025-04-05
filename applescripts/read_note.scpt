on run argv
	tell application id "Cere"
		try
			
			set thePath to ""
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
					
					if argName is "path" then
						set thePath to argValue
					else if argName is "document" then
						set theDocument to argValue
					end if
				end if
			end repeat

			set myNote to find note in document theDocument with path thePath
			
			set theName to get value of (attribute of myNote named "Name")
			set theText to get value of (attribute of myNote named "Text")
			return "# " & theName & linefeed & linefeed & theText
		on error errMsg
			return "Failed to find note: " & errMsg
		end try
	end tell
end run