# -*- coding: utf-8 -*-



import thread
import sys
import gobject
import pygst

#pygst.require("0.10")

pygst.require("1.0")

import gst


# gst-launch-1.0 souphttpsrc location=http://ber.radiostream.de:36795 ! decodebin ! autoaudiosink

class Player:

    _station = None

    def __init__(self):

        gobject.threads_init()
        def start():
            loop = gobject.MainLoop()
            loop.run()
        thread.start_new_thread(start, ())

        self.__file = None
        
        self.pipe = gst.Pipeline(name="trad")

        self.src = gst.element_factory_make("souphttpsrc", "souphttpsrc")
        self.decode_bin = gst.element_factory_make("decodebin", "decodebin")
        self.autoaudiosink = gst.element_factory_make("autoaudiosink", "autoaudiosink")

        self.pipe.add(src)
        self.pipe.add(decode_bin)
        self.pipe.add(autoaudiosink)


        gst.element_link_many(src, decode_bin, autoaudiosink)

        #equalizer.set_property('band2', -24.0)

        #self.player = gst.element_factory_make("playbin", "player")
        #self.is_eos = False
        #self.is_error = False

        self.bus = self.pipe.get_bus()
        self.bus.enable_sync_message_emission()


        self.bus.add_signal_watch()
        self.bus.connect("message", self._handle_message)

        self.playing  = False
        self.cached_time = False

        self.pause()


    def add_station(self, station):
        self._station = station
        self.pipe.set_state(gst.STATE_NULL)
        self.src.set_property("location", station['uri'])

    def play(self):
        if self._station is not None:
            self.pipe.set_state(gst.STATE_PLAYING)
            self.is_eos = False
            self.is_error = False

    def stop(self):
        if self._station is not None:
            self.pipe.set_state(gst.STATE_PAUSED)


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