#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import time
import thread

import urllib2

from PyQt4 import QtGui, QtCore


#from player import Player

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




#
# gst-launch-1.0 -v playbin uri=http://ber.radiostream.de:36795


class ParseConfigFile():
    
    def __init__(self, file_name):
        self.file_name = file_name

    def get_settings(self):
        fp = open(self.file_name, 'r')
        if fp is None:
            return []
        else:
            data = json.load(fp)
            print data
            fp.close()
            return data



class ActionMenu(QtGui.QAction):

    def __init__(self, data, parent=None):
        super(ActionMenu, self).__init__(data['name'], parent)
        self._data = data

        self.triggered.connect(self._set_station)

    def __str__(self):
        return _data['name']

    def _set_station(self):
        self.emit(QtCore.SIGNAL('set_station'), self._data)



class UpdateTrackName(QtCore.QThread):
    """Класс обновляет название выбранной песни
    """
    def __init__(self, parent=None):
        super(UpdateTrackName, self).__init__(parent)
        self._parent = parent

    def run(self):
        while True:
            time.sleep(1)
            title = None
            if self._parent.active_station is not None:
                stream_url = self._parent.active_station['uri']#sys.argv[1] or 'http://ber.radiostream.de:36795'

                #print('URL', stream_url)
                request = urllib2.Request(stream_url)
                try:
                    request.add_header('Icy-MetaData', 1)
                    response = urllib2.urlopen(request)
                    icy_metaint_header = response.headers.get('icy-metaint')
                    if icy_metaint_header is not None:
                        metaint = int(icy_metaint_header)
                        read_buffer = metaint+255
                        content = response.read(read_buffer)
                        title = content[metaint:].split("'")[1]
                        #print title
                        
                    #print response
                except:
                    print 'Error'
            self._parent.set_title_track(title)


class MenuApp(QtGui.QMenu):
    
    _active_station = None
    _is_playning = False


    def __init__(self, settings = [], parent=None):
        
        super(MenuApp, self).__init__("TrayRadio", parent)

        self._player = Player();
        
        # Название станции
        self._station_play_control = QtGui.QAction(u'Не выбранно', self)
        self.connect(self._station_play_control, QtCore.SIGNAL('triggered()'), self._play_and_stop)
        self.addAction(self._station_play_control)
        self.addSeparator()

        # Название трека
        self._track_name = QtGui.QAction(u'No name', self)
        self._track_name.setEnabled(False)
        self.addAction(self._track_name)
        self.addSeparator()

        for s in settings:
            genre_menu = QtGui.QMenu(s['genre'], self)
            for station in s['stations']:
                action_menu_item = ActionMenu(station, self)
                self.connect(action_menu_item, QtCore.SIGNAL('set_station'), self._set_station )
                genre_menu.addAction(action_menu_item)

            self.addMenu(genre_menu)
        self.addSeparator()

        action_settings = QtGui.QAction(u'Настройки', self)
        self.addAction(action_settings)

        action_record = QtGui.QAction(u'Запись трансляции', self)
        self.addAction(action_record)

        self.addSeparator()
        
        action_about = QtGui.QAction(u'О программе', self)
        self.addAction(action_about)

        action_exit = QtGui.QAction(u'Выход', self)
        self.addAction(action_exit)
        self.connect(action_exit, QtCore.SIGNAL('triggered()'), self.signal_close_app)


        self.thread_updater_track_name = UpdateTrackName(self)
        self.thread_updater_track_name.start()

    def set_title_track(self, title):
        text = "Playing: {0}".format(title or 'No name')
        self._track_name.setText(text)

    @property
    def active_station(self):
        return self._active_station

    def _change_station(self):
        name = self._active_station['name']
        
        if self._is_playning:
            title = 'Turn on'
        else:
            title = 'Turn off'

        text = "{0} {1}".format(title, name)
        self._station_play_control.setText(text)


    def _play_and_stop(self):
        self._is_playning = not self._is_playning

        if self._active_station is not None:
            if self._is_playning:
                self._player.stop()
            else:
                self._player.play()

        self._change_station()


    def _set_station(self, station):
        self._is_playning = True
        self._active_station = station
        self._player.add_station(station)
        self._player.play()
        self._change_station()


    def signal_close_app(self):
        QtGui.QApplication.quit()
        


class SystemTrayIcon(QtGui.QSystemTrayIcon):

    def __init__(self, settings, parent=None):
        super(SystemTrayIcon, self).__init__(parent)
        self.setIcon(QtGui.QIcon("icons/radio-icon.png"))
        
        self.menu = MenuApp(settings)

        self.activated.connect(self.click_trap)

    def click_trap(self, value):
        if value == self.Trigger: #left click!
            pos = self.geometry().topRight()
            x, y = pos.x() - self.menu.width()/2, pos.y() - self.menu.height()
            self.menu.move(x, y)
            self.menu.show()


if __name__ == '__main__':

    config = ParseConfigFile('settings/settings.json')
    config_data = config.get_settings()
    
    app = QtGui.QApplication([])
    tray = SystemTrayIcon(config_data)
    tray.show()
    app.exec_()
