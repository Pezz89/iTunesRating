on is_running(appName)
	tell application "System Events" to (name of processes) contains appName
end is_running

on get_current_track_info()
	tell application "iTunes"
		set current_track to the current track
		set track_album to the album of the current track
		set track_artist to the artist of the current track
		set track_comments to the comment of the current track
		set track_name to the name of the current track
		set track_rating to the rating of the current track
	end tell
	return {album:track_album, artist:track_artist, track_name:track_name}
end get_current_track_info

on set_current_track_rating(track_rating)
	tell application "iTunes"
		set rating of current track to track_rating
	end tell
end set_current_track_rating

on get_album_artwork(directory)
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
end get_album_artwork
