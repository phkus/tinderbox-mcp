on run argv
	tell application id "Cere"
		try

			set attributeName to ""
			set attributeValue to ""
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
					
					-- Assign the value to the appropriate variable
					if argName is "path" then
						set thePath to argValue
					else if argName is "document" then
						set theDocument to argValue
					else if argName is "attribute" then
						set attributeName to argValue
					else if argName is "value" then
						set attributeValue to argValue
					end if
				end if
			end repeat
			
			set myNote to find note in document theDocument with path thePath
			
			-- Add code to use attributeName and attributeValue if they’re provided
			if attributeName is not equal to "" and attributeValue is not equal to "" then
				-- Set the specified attribute to the specified value using correct Tinderbox syntax
				set value of (attribute of myNote named attributeName) to attributeValue
				return "Successfully updated attribute '" & attributeName & "' to '" & attributeValue & "' for note '" & thePath & "'"
			end if
			
		end try
	end tell
end run