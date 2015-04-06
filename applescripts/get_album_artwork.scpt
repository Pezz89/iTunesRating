on run(directory)
	tell application "iTunes" to tell artwork 1 of current track
	    set d to raw data
	    if format is "class PNG"  then
		set x to "png"
	    else
		set x to "jpg"
	    end if
	end tell

	(((directory) as text) & "cover." & x)
	set b to open for access file result with write permission
	set eof b to 0
	write d to b
	close access b
	return (((directory) as text) & "cover." & x)
end run
