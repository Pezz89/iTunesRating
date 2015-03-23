import wx
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
        self.start()    # start the thread

    #----------------------------------------------------------------------
    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread.
        program_running = True
        self.iTunes = iTunesBridge()
        current_track = None
        artwork = None
        Publisher.subscribe(self.setRating, "rate")
        self.set_rating = False
        prev_track = None
        while(program_running):
            if self.iTunes.is_running():
                current_track = self.iTunes.get_current_track_info()
                update_artwork = False
                if prev_track != current_track:
                    update_artwork = True
                    artwork = (
                    self.iTunes.get_artwork(os.getcwd())
                    )
                    if not artwork:
                        artwork = "/Users/samperry/Python_Projects/itunes_v2/nocover.png"
                if self.set_rating:
                    self.iTunes.set_current_track_rating(self.rating)
                
            prev_track = current_track
            time.sleep(0.25)
            wx.CallAfter(self.postInfo, current_track, artwork, update_artwork)
 
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
        #Create the main window?
        super(MainWindow, self).__init__(
            parent,
            title=title,
        )
        #--------------------------------------------------------------
        #Create a file manu
        filemenu = wx.Menu()
        
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
        for i in xrange(5):
            #Store each button object in a list
            self.buttons.append(wx.Button(self, -1, "&" + str(i+1)))
            #Add each button object to the sizer
            self.button_sizer.Add(self.buttons[i], 1, wx.EXPAND)
            self.buttons[i].Bind(wx.EVT_BUTTON, self.OnButton)
        
        #Create a text object
        self.artist_text = wx.StaticText(self, label="Artist:\t")
        self.song_text = wx.StaticText(self, label="Title:\t")
        self.album_text = wx.StaticText(self, label="Album:\t")
        
        for i in (self.song_text, self.artist_text, self.album_text):
            self.text_sizer.Add(i, 1, wx.EXPAND)
        self.info_sizer.Add(self.text_sizer, 1, wx.EXPAND)
        self.info_sizer.Add(self.button_sizer, 1, wx.EXPAND)

        #--------------------------------------------------------------
        #Specify the maximum size of the album artwork
        self.current_artwork = "nocover.png"        
        img = wx.Image("nocover.png", wx.BITMAP_TYPE_ANY)
        img = img.Scale(120,120)
        self.icon = wx.StaticBitmap(self, bitmap=wx.BitmapFromImage(img))
        self.main_sizer.Add(self.icon, 1, wx.EXPAND)
        self.main_sizer.Add(self.info_sizer, 3, wx.EXPAND)
        #Select the sizer to use for the main window
        self.SetSizer(self.main_sizer)
        self.SetAutoLayout(1)
        #Fit sizer 1 to window
        self.SetSizerAndFit(self.main_sizer)

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
            if update_artwork:
                if not artwork:
                    img = wx.Image("nocover.jpg", wx.BITMAP_TYPE_ANY)
                    img = img.Scale(120,120)
                    self.icon = wx.StaticBitmap(self, bitmap=wx.BitmapFromImage(img))
                else:
                    img = wx.Image(artwork, wx.BITMAP_TYPE_ANY)
                    img = img.Scale(120,120)
                    self.icon = wx.StaticBitmap(self, bitmap=wx.BitmapFromImage(img))
                    self.icon.Refresh()

#--------------------------------------------------------------
app = wx.App(False)
frame = MainWindow(None, title="iTunes Rating")
frame.Show()
app.MainLoop()
