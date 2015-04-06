on run()
	tell application "iTunes"
		set current_track to the current track
		set track_album to the album of the current track
		set track_artist to the artist of the current track
		set track_comments to the comment of the current track
		set track_name to the name of the current track
		set track_rating to the rating of the current track
		set track_duration to the duration of the current track
		set track_finish to the finish of the current track
		set track_start to the start of the current track
		set track_position to the player position
	end tell
	return {album:track_album, artist:track_artist, track_name:track_name, rating:track_rating, duration:track_duration, finish:track_finish, start:track_start, position:track_position}
end run
