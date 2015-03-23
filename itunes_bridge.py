#!/usr/bin/env python

import applescript
import os

class iTunesBridge:
    def __init__(self, script_file="./itunes_scripts.scpt"):
        with open("./itunes_scripts.scpt") as script_file:
            script_data = ''.join([line for line in script_file])
        self.as_bridge = applescript.AppleScript(script_data)
        self.current_track = None

    def is_running(self):
        return self.as_bridge.call("is_running", "iTunes")
    
    def set_current_track_rating(self, rating):
        """
        Try to set the rating of the current track
        Return True if succesful else False
        """
        try:
            self.as_bridge.call("set_current_track_rating", rating)
            return True
        except applescript.ScriptError:
            return False

    def get_artwork(self, directory):
        directory = os.path.realpath(directory).replace('/', ':')[1:]
        try:
            artwork = self.as_bridge.call("get_album_artwork", directory+':')
        except applescript.ScriptError:
            return None
        artwork = '/'+artwork.replace(':', '/')
        return artwork

    def get_current_track_info(self):
        try:
            track_info = self.as_bridge.call("get_current_track_info")
        except applescript.ScriptError:
            return None
        return track_info


def main():
    iTunes = iTunesBridge()
    print iTunes.is_running()
    iTunes.get_current_track_info()

if __name__ == "__main__":
    main()
