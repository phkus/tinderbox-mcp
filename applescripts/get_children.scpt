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
					
					-- Assign the value to the appropriate variable
					if argName is "path" then
						set thePath to argValue
					else if argName is "document" then
						set theDocument to argValue
					end if
				end if
			end repeat
			
			set myNote to find note in document theDocument with path thePath
			
			set theChildren to notes in myNote
			
			-- Format as JSON array of dictionaries
			set jsonArray to "["
			repeat with i from 1 to count of theChildren
			    set theChild to item i of theChildren
			    set childPath to value of (attribute of theChild named "Path")
			    set childChildCount to value of (attribute of theChild named "ChildCount")
    
			    -- Create dictionary with path and childCount
			    set jsonDict to "{\"Path\": \"" & childPath & "\", \"ChildCount\": " & childChildCount & "}"
    
			    -- Add to array with comma if not the last item
			    set jsonArray to jsonArray & jsonDict
			    if i < (count of theChildren) then
			        set jsonArray to jsonArray & ", "
			    end if
			end repeat
			set jsonArray to jsonArray & "]"
			return jsonArray
		end try
	end tell
end run
