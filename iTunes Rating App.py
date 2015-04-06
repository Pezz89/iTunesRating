import wx
import yappi
import os
import time
from threading import Thread
from wx.lib.pubsub import pub as Publisher
from itunes_bridge import iTunesBridge

#--------------------------------------------------------------
class iTunes_com_thread(Thread):
    """A class for communications with itunes"""
    def __init__(self):
        """Init Thread Class."""
        Thread.__init__(self)
        self.setDaemon(1)
        self.start()    # start the thread

    #----------------------------------------------------------------------
    def run(self):
        """Run Worker Thread."""
        
        #----------------------------------------------------------------------
        #Declare variables
        program_running = True
        current_track = None
        artwork = None
        self.set_rating = False
        prev_track = None
        
        #Create bridge to iTunes for sending and recieving data to/from itunes
        self.iTunes = iTunesBridge()
        
        #Subscribe to the rate publisher for messages about updating ratings
        Publisher.subscribe(self.setRating, "rate")
        
        #Main loop 
        while(program_running):
            #Only execute itunes code if it is running
            if self.iTunes.is_running():
                #Get dictionary of information about the current track
                current_track = self.iTunes.get_current_track_info()
                #If the track has changed since the previous loop, update the
                #displayed artwork
                update_artwork = False
                if prev_track != current_track:
                    update_artwork = True
                    #Get the file location of the new artwork to display
                    artwork = (
                    self.iTunes.get_artwork(os.getcwd())
                    )
                    #If the track has no artwork then display the no artwork
                    #picture
                    if not artwork:
                        artwork = '/'.join((os.getcwd(), "nocover.png"))
                #If the rating needs to be updated then set it to the updated
                #value
                if self.set_rating:
                    self.iTunes.set_current_track_rating(self.rating)
                    self.set_rating = False
                
            prev_track = current_track
            #Update the display with the new information
            wx.CallAfter(self.postInfo, current_track, artwork, update_artwork)
            #pause loop briefly
            time.sleep(0.25)
 
    #----------------------------------------------------------------------
    def postInfo(self, current_track, artwork, update_artwork):
        """Send track info to the GUI"""
        Publisher.sendMessage("update", data = current_track, data2 = artwork,
                              data3 = update_artwork)
    
    def setRating(self, data):
        """Set rating of the current track"""
        self.set_rating = True
        self.rating = data * 20

#--------------------------------------------------------------
class MainWindow(wx.Frame):
    def __init__(self, parent, title=''):
        #Create the main window
        super(MainWindow, self).__init__(
            parent,
            title=title,
            style= wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.STAY_ON_TOP |
            wx.RESIZE_BORDER
        )
        #--------------------------------------------------------------
        #Create a file manu
        filemenu = wx.Menu()
        
        #Create a panel
        self.panel = wx.Panel(self)
        self.flashing_panel = False
        self.flashbool = False
        #Define menu items
        menu_about = filemenu.Append(
            wx.ID_ABOUT, 
            "&About", 
            "Show information about this program"
        )
        menu_exit = filemenu.Append(
            wx.ID_EXIT,
            "E&XIT",
            "End the program"
        )

        #Create the menu bar to place the filemenu in
        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        #Add the menu bar to the frame
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.OnAbout, menu_about)
        self.Bind(wx.EVT_MENU, self.OnExit, menu_exit)
    

        #set the directory variable to the current directory of this script
        self.dirname = os.getcwd()

        #Create 3 sizers to arange objects in
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.info_sizer = wx.BoxSizer(wx.VERTICAL)
        self.text_sizer = wx.BoxSizer(wx.VERTICAL)
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
       
        #Create a list to store rating buttons in
        self.buttons = []
        for i in xrange(6):
            #Store each button object in a list
            self.buttons.append(wx.Button(
                self, 
                -1, 
                "&" + str(i), 
                style=wx.BU_EXACTFIT,
                size = (40, 28)
            ))
            #Add each button object to the sizer
            self.button_sizer.AddStretchSpacer(prop = 1)
            self.button_sizer.Add(self.buttons[i], 0, wx.ALIGN_CENTER)
            self.button_sizer.AddStretchSpacer(prop = 1)
            self.buttons[i].Bind(wx.EVT_BUTTON, self.OnButton)
        
        #Create a text object
        self.artist_text = wx.StaticText(self.panel, label="Artist:\t")
        self.song_text = wx.StaticText(self.panel, label="Title:\t")
        self.album_text = wx.StaticText(self.panel, label="Album:\t")
        self.rating_text = wx.StaticText(self.panel, label="Rating:\t")
        
        for i in (
            self.song_text, 
            self.artist_text, 
            self.album_text,
            self.rating_text
        ):
            self.text_sizer.Add(i, 1, wx.EXPAND)
        self.info_sizer.Add(self.text_sizer, wx.ALIGN_LEFT)
        self.info_sizer.Add(self.button_sizer, wx.ALIGN_LEFT)

        #--------------------------------------------------------------
        #Specify the maximum size of the album artwork
        self.current_artwork = "nocover.png"        
        img = wx.Image("nocover.png", wx.BITMAP_TYPE_ANY)
        img = img.Scale(120,120)
        self.icon = wx.StaticBitmap(self, bitmap=wx.BitmapFromImage(img))
        
        #Add the artwork and the information sizer to the main sizer
        self.main_sizer.Add(self.icon, wx.ALIGN_LEFT)
        self.main_sizer.Add(self.info_sizer, wx.ALIGN_LEFT)
        
        #Select the sizer to use for the main window
        self.SetAutoLayout(1)
        #Fit sizer 1 to window
        self.panel.SetSizerAndFit(self.main_sizer)
 
        sizer = wx.BoxSizer(wx.HORIZONTAL | wx.ALIGN_LEFT)
        sizer.Add(self.panel, wx.EXPAND)
        self.SetSizerAndFit(sizer)
        self.SetMinSize(self.GetBestSize())
        self.SetMaxSize((-1, self.GetBestSize()[1]))
        #initialize comunication thread
        iTunes_com_thread()
        
        #Create publisher reciever to recieve messages from thread
        Publisher.subscribe(self.updateDisplay, "update")
        
        self.Show()

    #--------------------------------------------------------------
    def OnAbout(self, event):
        """Show information about the program"""
        #Create a dialog box containing theinformation about the program
        dlg = wx.MessageDialog(self, "iTunes Rating App", "Created by Sam Perry")
        
        #Show the dialog
        dlg.ShowModal()
        #Destroy when finished
        dlg.Destroy()
    
    #--------------------------------------------------------------
    def OnExit(self, event):
        """Close the frame"""
        self.Close(True)

    #--------------------------------------------------------------
    def OnButton(self, event):
        """Set the rating of a track based on the button pressed"""
        btn = event.GetEventObject()
        rating = int(btn.GetLabelText())
        wx.CallAfter(Publisher.sendMessage, "rate", data = rating)
    
    #--------------------------------------------------------------
    def updateDisplay(self, data, data2, data3):
        """Receives data from thread and updates the display"""
        t = data
        artwork = data2
        update_artwork = data3
        if isinstance(t, dict):
            self.artist_text.SetLabel("Artist:\t" + t["artist"])
            self.song_text.SetLabel("Title:\t" + t["track_name"])
            self.album_text.SetLabel("Album:\t" + t["album"])
            self.rating_text.SetLabel("Rating:\t" + str(t["rating"]/20))
            if update_artwork:
                if not artwork:
                    img = wx.Image("nocover.jpg", wx.BITMAP_TYPE_ANY)
                    img = img.Scale(120,120)
                    self.icon = wx.StaticBitmap(self, bitmap=wx.BitmapFromImage(img))
                else:
                    img = wx.Image(artwork, wx.BITMAP_TYPE_ANY)
                    img = img.Scale(120,120)
                    self.icon = wx.StaticBitmap(self, bitmap=wx.BitmapFromImage(img))
            if t["duration"] - t["position"] <= 30:
                if self.flashbool:
                   self.panel.SetBackgroundColour(wx.NullColour)
                   self.panel.Refresh()
                   self.flashbool = False
                else:
                   self.panel.SetBackgroundColour("Yellow")
                   self.panel.Refresh()
                   self.flashbool = True
            else:
                   self.panel.SetBackgroundColour(wx.NullColour)
                   self.panel.Refresh()


#--------------------------------------------------------------
def main():
    app = wx.App(False)
    frame = MainWindow(None, title="iTunes Rating")
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    yappi.start()
    main()
    yappi.get_func_stats().print_all()
    yappi.get_thread_stats().print_all()
