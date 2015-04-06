on run(track_rating)
	tell application "iTunes"
		set rating of current track to track_rating
	end tell
end run
