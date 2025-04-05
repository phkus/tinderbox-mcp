on run argv
  tell application id "Cere"
    try
      set theTitle to ""
      set theText to ""
      set theContainer to ""
      set theDocument to "Dissertation"

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
          if argName is "title" then
            set theTitle to argValue
          else if argName is "text" then
            set theText to argValue
          else if argName is "document" then
            set theDocument to argValue
          else if argName is "parent" then
            set theContainer to argValue
            if not (theContainer ends with "/") then
              set theContainer to theContainer & "/"
            end if
          end if
        end if
      end repeat

      set myNote to make new note in document theDocument
      set value of (attribute of myNote named "Name") to theTitle
      set value of (attribute of myNote named "Text") to theText

      if theContainer is not "" then
        try
          set value of (attribute of myNote named "Container") to theContainer
        on error
          -- error handling
        end try
      end if

      return "Successfully created new note '" & theTitle & "' in Tinderbox"
    on error errMsg
      return "Failed to create note: " & errMsg
    end try
  end tell
end run