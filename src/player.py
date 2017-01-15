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
        #self.souphttpsrc.set_property("location", "http://ber.radiostream.de:36795")
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
        if self._station is not None:
            self.player.set_state(gst.State.PAUSED)

    """
    def add_station(self, station):
        self._station = station
        self.player.set_state(gst.STATE_NULL)
        self.src.set_property("location", station['uri'])

    def play(self):
        if self._station is not None:
            self.player.set_state(gst.STATE_PLAYING)
            self.is_eos = False
            self.is_error = False

    def stop(self):
        if self._station is not None:
            self.player.set_state(gst.STATE_PAUSED)


    def _handle_message(self, bus, msg):
        if msg.type == gst.MESSAGE_EOS:
            self.is_eos = True
            self.player.set_state(gst.STATE_NULL)

        elif msg.type == gst.MESSAGE_ERROR:
            self.is_error = False
            self.player.set_state(gst.STATE_NULL)
            (err, debug) = msg.parse_error()
            
            sys.stderr.write("Error: %s  | %s" % (err, debug))

    """
"""
from gi.repository import GObject, Gst, Gtk
class Player:

    _station = None

    def __init__(self):

        GObject.threads_init()
        def start():
            loop = GObject.MainLoop()
            loop.run()
        thread.start_new_thread(start, ())

        self.__file = None
        
        self.pipe = gst.Pipeline(name="trad")

        #self.src = gst.element_factory_make("souphttpsrc", "souphttpsrc")
        #self.decode_bin = gst.element_factory_make("decodebin", "decodebin")
        #self.autoaudiosink = gst.element_factory_make("autoaudiosink", "autoaudiosink")

        #self.pipe.add(src)
        #self.pipe.add(decode_bin)
        #self.pipe.add(autoaudiosink)
        self.player = gst.element_factory_make("playbin", "player")

        gst.element_link_many(src, decode_bin, autoaudiosink)

        #equalizer.set_property('band2', -24.0)
        #self.player = gst.element_factory_make("playbin", "player")
        #self.is_eos = False
        #self.is_error = False

        self.bus = self.player.get_bus()
        self.bus.enable_sync_message_emission()


        self.bus.add_signal_watch()
        self.bus.connect("message", self._handle_message)

        self.playing  = False
        self.cached_time = False

        self.pause()


    def add_station(self, station):
        self._station = station
        self.player.set_state(gst.STATE_NULL)
        self.src.set_property("location", station['uri'])

    def play(self):
        if self._station is not None:
            self.player.set_state(gst.STATE_PLAYING)
            self.is_eos = False
            self.is_error = False

    def stop(self):
        if self._station is not None:
            self.player.set_state(gst.STATE_PAUSED)


    def _handle_message(self, bus, msg):
        if msg.type == gst.MESSAGE_EOS:
            self.is_eos = True
            self.player.set_state(gst.STATE_NULL)

        elif msg.type == gst.MESSAGE_ERROR:
            self.is_error = False
            self.player.set_state(gst.STATE_NULL)
            (err, debug) = msg.parse_error()
            
            sys.stderr.write("Error: %s  | %s" % (err, debug))



"""
"""
import thread
import sys
import gobject
import pygst

pygst.require("0.10")

import gst

class Player:
    def __init__(self):

        gobject.threads_init()
        def start():
            loop = gobject.MainLoop()
            loop.run()
        thread.start_new_thread(start, ())

        self.__file = None
        self.player = gst.element_factory_make("playbin", "player")
        self.is_eos = False
        self.is_error = False

        self.bus = self.player.get_bus()
        self.bus.enable_sync_message_emission()


        self.bus.add_signal_watch()
        self.bus.connect("message", self._handle_message)

        self.playing  = False
        self.cached_time = False

        self.pause()

    # добавляю файл на воспроизведение
    def add_station(self, url):
        self.__file = url
        self.player.set_state(gst.STATE_NULL)
        self.player.set_property('uri', self.__file)
        
    def pause(self):
        self.playing  = False
        self.player.set_state(gst.STATE_PAUSED)
        self.is_eos = False

    def play(self):
        if self.__file is not None:
            self.playing  = True
            self.player.set_state(gst.STATE_PLAYING)
            self.is_eos = False
            self.is_error = False

    def set_sound_volume(self, volume):
        self.player.set_property('volume', volume)

    def get_sound_volume(self):
        return self.player.get_property('volume')


    def _get_state(self):
        return self.player.get_state()[1]


    
    # возврат времени выполнения, в виде кортежа. первое число текущая позиция, второе число - общее время
    def time(self):
        if self.__file is not None:
            fmt = gst.Format(gst.FORMAT_TIME)
            try:
                pos = self.player.query_position(fmt, None)[0]/(10**9)
                length = self.player.query_duration(fmt, None)[0]/(10**9)
                self.cached_time = (pos, length)
                return (pos, length)

            except gst.QueryError:
                if self.playing and self.cached_time:
                    return self.cached_time
                else:
                    return (0, 0)
    

    # обработка сообщений 
    def _handle_message(self, bus, msg):
        if msg.type == gst.MESSAGE_EOS:
            self.is_eos = True
            self.player.set_state(gst.STATE_NULL)

        elif msg.type == gst.MESSAGE_ERROR:
            self.is_error = False
            self.player.set_state(gst.STATE_NULL)
            (err, debug) = msg.parse_error()
            
            sys.stderr.write("Error: %s  | %s" % (err, debug))

    
    # пеермещщение по записи
    def seek(self, position):
        cur_pos, cur_len = self.time()
        if position > cur_len:
            #self.stop()
            return

        fmt = gst.Format(gst.FORMAT_TIME)
        ns = position * 10**9 # convert to nanoseconds
        self.player.seek_simple(fmt, gst.SEEK_FLAG_FLUSH, ns)

"""
 

"""
import thread
import sys
import gobject
import pygst

#pygst.require("1.0")
#import gi
#gi.require_version('Gst', '1.0')

pygst.require("0.10")

import gst
"""
"""
import gi
gi.require_version('Gst', '1.0')
import thread
import sys
from gi.repository import GObject
import pygst

import gst
"""
# gst-launch-1.0 souphttpsrc location=http://ber.radiostream.de:36795 ! decodebin ! autoaudiosink

"""
class Player:

    _station = None

    def __init__(self):

        GObject.threads_init()
        def start():
            loop = GObject.MainLoop()
            loop.run()
        thread.start_new_thread(start, ())

        self.__file = None
        
        self.pipe = gst.Pipeline(name="trad")

        #self.src = gst.element_factory_make("souphttpsrc", "souphttpsrc")
        #self.decode_bin = gst.element_factory_make("decodebin", "decodebin")
        #self.autoaudiosink = gst.element_factory_make("autoaudiosink", "autoaudiosink")

        #self.pipe.add(src)
        #self.pipe.add(decode_bin)
        #self.pipe.add(autoaudiosink)
        self.player = gst.element_factory_make("playbin", "player")

        gst.element_link_many(src, decode_bin, autoaudiosink)

        #equalizer.set_property('band2', -24.0)
        #self.player = gst.element_factory_make("playbin", "player")
        #self.is_eos = False
        #self.is_error = False

        self.bus = self.player.get_bus()
        self.bus.enable_sync_message_emission()


        self.bus.add_signal_watch()
        self.bus.connect("message", self._handle_message)

        self.playing  = False
        self.cached_time = False

        self.pause()


    def add_station(self, station):
        self._station = station
        self.player.set_state(gst.STATE_NULL)
        self.src.set_property("location", station['uri'])

    def play(self):
        if self._station is not None:
            self.player.set_state(gst.STATE_PLAYING)
            self.is_eos = False
            self.is_error = False

    def stop(self):
        if self._station is not None:
            self.player.set_state(gst.STATE_PAUSED)


    def _handle_message(self, bus, msg):
        if msg.type == gst.MESSAGE_EOS:
            self.is_eos = True
            self.player.set_state(gst.STATE_NULL)

        elif msg.type == gst.MESSAGE_ERROR:
            self.is_error = False
            self.player.set_state(gst.STATE_NULL)
            (err, debug) = msg.parse_error()
            
            sys.stderr.write("Error: %s  | %s" % (err, debug))
"""

"""
    # добавляю файл на воспроизведение
    def add_track(self, url):
        self.__file = url
        self.player.set_state(gst.STATE_NULL)
        self.player.set_property('uri', self.__file)
        
    def pause(self):
        self.playing  = False
        self.player.set_state(gst.STATE_PAUSED)
        self.is_eos = False

    def play(self):
        if self.__file is not None:
            self.playing  = True
            self.player.set_state(gst.STATE_PLAYING)
            self.is_eos = False
            self.is_error = False

    def set_sound_volume(self, volume):
        self.player.set_property('volume', volume)

    def get_sound_volume(self):
        return self.player.get_property('volume')

    def _get_state(self):
        #Returns the current state flag of the playbin.
        return self.player.get_state()[1]


    # возврат времени выполнения, в виде кортежа. первое число текущая позиция, второе число - общее время
    def time(self):
        if self.__file is not None:
            fmt = gst.Format(gst.FORMAT_TIME)
            try:
                pos = self.player.query_position(fmt, None)[0]/(10**9)
                length = self.player.query_duration(fmt, None)[0]/(10**9)
                self.cached_time = (pos, length)
                return (pos, length)

            except gst.QueryError:
                if self.playing and self.cached_time:
                    return self.cached_time
                else:
                    return (0, 0)

    # обработка сообщений 
    def _handle_message(self, bus, msg):
        if msg.type == gst.MESSAGE_EOS:
            self.is_eos = True
            self.player.set_state(gst.STATE_NULL)

        elif msg.type == gst.MESSAGE_ERROR:
            self.is_error = False
            self.player.set_state(gst.STATE_NULL)
            (err, debug) = msg.parse_error()
            
            sys.stderr.write("Error: %s  | %s" % (err, debug))

    # пеермещщение по записи
    def seek(self, position):
        cur_pos, cur_len = self.time()
        if position > cur_len:
            #self.stop()
            return

        fmt = gst.Format(gst.FORMAT_TIME)
        ns = position * 10**9 # convert to nanoseconds

        self.player.seek_simple(fmt, gst.SEEK_FLAG_FLUSH, ns)

"""