#!/usr/bin/env python

import applescript
import os

class iTunesBridge:
    def __init__(self):
        with open("./applescripts/is_running.scpt", 'r') as is_running_file,\
        open("./applescripts/get_track_info.scpt", 'r') as track_info_file,\
        open("./applescripts/set_current_track_rating.scpt", 'r') as\
        set_rating_file, open("./applescripts/get_album_artwork.scpt") as\
        album_artwork_file:
            is_running_data = ''.join([line for line in is_running_file])
            track_info_data = ''.join([line for line in track_info_file])
            set_rating_data = ''.join([line for line in set_rating_file])
            album_artwork_data = ''.join([line for line in album_artwork_file])
        self.is_running_bridge = applescript.AppleScript(is_running_data)
        self.track_info_bridge = applescript.AppleScript(track_info_data)
        self.set_rating_bridge = applescript.AppleScript(set_rating_data)
        self.album_artwork_bridge = applescript.AppleScript(album_artwork_data)
        self.current_track = None

    def is_running(self):
        return self.is_running_bridge.run("iTunes")
    
    def set_current_track_rating(self, rating):
        """
        Try to set the rating of the current track
        Return True if succesful else False
        """
        try:
            self.set_rating_bridge.run(rating)
            return True
        except applescript.ScriptError:
            return False

    def get_artwork(self, directory):
        directory = os.path.realpath(directory).replace('/', ':')[1:]
        try:
            artwork = self.album_artwork_bridge.run(directory+':')
        except applescript.ScriptError:
            return None
        artwork = '/'+artwork.replace(':', '/')
        return artwork

    def get_current_track_info(self):
        try:
            track_info = self.track_info_bridge.run()
        except applescript.ScriptError:
            return None
        return track_info

def main():
    print "Nothing in main"

if __name__ == "__main__":
    main()
