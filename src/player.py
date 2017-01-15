# -*- coding: utf-8 -*-
import thread
import gi
gi.require_version('Gst', '1.0')
#gi.require_version('Gtk', '3.0')

from gi.repository import GObject, Gst#, Gtk

# Initializing threads used by the Gst various elements
GObject.threads_init()
#Initializes the GStreamer library, setting up internal path lists, registering built-in elements, and loading standard plugins.
Gst.init(None)

class Player:
    
    _station = None

    def __init__(self):

        def start():
            self.mainloop = GObject.MainLoop()
            #loop = GObject.MainLoop()
            #loop.run()
            self.mainloop.run()
        thread.start_new_thread(start, ())

        #Creating the gst pipeline we're going to add elements to and use to play the file
        self.pipeline = Gst.Pipeline.new("mypipeline")

        #creating the souphttpsrc element, and adding it to the pipeline
        self.souphttpsrc = Gst.ElementFactory.make("souphttpsrc", "souphttpsrc")
        self.pipeline.add(self.souphttpsrc)
        
        #creating and adding the decodebin element , an "automagic" element able to configure itself to decode pretty much anything
        self.decode = Gst.ElementFactory.make("decodebin", "decode")
        self.pipeline.add(self.decode)
        #connecting the decoder's "pad-added" event to a handler: the decoder doesn't yet have an output pad (a source), it's created at runtime when the decoders starts receiving some data
        self.decode.connect("pad-added", self._decode_src_created) 
        
        #setting up (and adding) the alsasin, which is actually going to "play" the sound it receives
        self.sink = Gst.ElementFactory.make("autoaudiosink", "autoaudiosink")
        self.pipeline.add(self.sink)

        #linking elements one to another (here it's just the souphttpsrc - > decoder link , the decoder -> sink link's going to be set up later)
        self.souphttpsrc.link(self.decode)
    
    #handler taking care of linking the decoder's newly created source pad to the sink
    def _decode_src_created(self, element, pad):
        pad.link(self.sink.get_static_pad("sink"))    
        
    #running the shit
    def play(self):
        self.pipeline.set_state(Gst.State.PLAYING)

    def add_station(self, station):
        self._station = station
        self.pipeline.set_state(Gst.State.NULL)
        self.souphttpsrc.set_property("location", station['uri'])
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        #if self._station is not None:
        self.pipeline.set_state(Gst.State.PAUSED)
