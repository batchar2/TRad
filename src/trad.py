#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import shutil

import thread
import urllib2

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst#, Gtk


from PyQt4 import QtGui, QtCore

# Initializing threads used by the Gst various elements
#Initializes the GStreamer library, setting up internal path lists, registering built-in elements, and loading standard plugins.
#Gst.init(None)



class Player:
    """
    Реализуется плеер на gstreamer. 
    """
    def __init__(self):
        def start():
            """
            В отдельном потоке запускаю mainloop Gstreamer'а
            """
            self._mainloop = GObject.MainLoop()
            self._mainloop.run()

        Gst.init()
        GObject.threads_init()
            
        thread.start_new_thread(start, ())

        self._play_bin = Gst.ElementFactory.make('playbin', 'player')
        if self._play_bin is not None:
            self._play_bin.set_property('volume', 1.0)
            self._play_bin.set_state(Gst.State.PAUSED)
        else:
            print("Ошибка! Плагин gstreamer playbin не найден!")

    def play(self):
        if self._play_bin is not None:
            self._play_bin.set_state(Gst.State.PLAYING)

    def set_station(self, uri):
        if self._play_bin is not None:
            self._play_bin.set_property('uri', uri) 
        
    def stop(self):
        print("STOP")
        if self._play_bin is not None:
            self._play_bin.set_state(Gst.State.PAUSED)        


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
    """
    Класс обновляет название песни на станции.
    """
    def __init__(self, parent=None):
        super(UpdateTrackName, self).__init__(parent)
        self._parent = parent


    def run(self):
        """
        Запрашиваем у радиостанции название трека.
        Для этого формируем специальный HTTP запрос
        """
        time_period = 5
        while True:
            time.sleep(time_period)
            title = None
            if self._parent.active_station is not None:
                stream_url = self._parent.active_station['uri']
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
                except:
                    print('Error')
            self._parent.set_title_track(title)


class MenuApp(QtGui.QMenu):    
    _active_station = None
    _is_playning = False

    def __init__(self, settings = [], parent=None):
        super(MenuApp, self).__init__("TrayRadio", parent)

        self._player = Player();

        self._add_menu_items()

        self.thread_updater_track_name = UpdateTrackName(self)
        self.thread_updater_track_name.start()


    def _add_menu_items(self):
        # Название станции
        self._station_play_control = QtGui.QAction(u'Не выбранно', self)
        self.connect(self._station_play_control, QtCore.SIGNAL('triggered()'), self._play_and_stop)
        self.addAction(self._station_play_control)
        self.addSeparator()

        # Название трека
        self._track_name = QtGui.QAction(u'Нет имени', self)
        self._track_name.setEnabled(False)
        self.addAction(self._track_name)
        self.addSeparator()

        # Добавляем станции из конфига
        for s in settings:
            genre_menu = QtGui.QMenu(s['genre'], self)
            for station in s['stations']:
                action_menu_item = ActionMenu(station, self)
                self.connect(action_menu_item, QtCore.SIGNAL('set_station'), self._set_station )
                genre_menu.addAction(action_menu_item)
            self.addMenu(genre_menu)
        self.addSeparator()

        action_settings = QtGui.QAction(u'Настройки', self)
        action_settings.setEnabled(False)
        self.addAction(action_settings)

        action_record = QtGui.QAction(u'Запись трансляции', self)
        action_record.setEnabled(False)
        self.addAction(action_record)

        self.addSeparator()
        
        action_about = QtGui.QAction(u'О программе', self)
        action_about.setEnabled(False)
        self.addAction(action_about)

        action_exit = QtGui.QAction(u'Выход', self)
        self.addAction(action_exit)
        self.connect(action_exit, QtCore.SIGNAL('triggered()'), self.signal_close_app)


    def set_title_track(self, title):
        text = u'Воспроизводится: {0}'.format(title or u'Нет имени')
        self._track_name.setText(text)


    @property
    def active_station(self):
        return self._active_station


    def _change_station(self):
        """
        Изменяем состояние: включено или выключено
        """
        name = self._active_station['name']
        if self._is_playning:
            title = u'Остановить'
        else:
            title = u'Запустить'
        text = u"{0} {1}".format(title, name)
        self._station_play_control.setText(text)


    def _play_and_stop(self):
        """
        Останавливаем или запускаем  воспроизведение
        """
        if self._active_station is not None:
            if self._is_playning:
                self._player.stop()
            else:
                self._player.play()
            self._is_playning = not self._is_playning

        self._change_station()


    def _set_station(self, station):
        """
        Устанавливаю проигрываимую станцию
        """
        self._is_playning = True
        self._active_station = station
        self._player.stop()
        self._player.set_station(station['uri'])
        self._player.play()
        self._change_station()


    def signal_close_app(self):
        """
        Завершаю приложение
        """
        QtGui.QApplication.quit()
        

class Tray(QtGui.QSystemTrayIcon):
    def __init__(self, settings, icon_path, parent=None):
        super(Tray, self).__init__(parent)
        self.setIcon(QtGui.QIcon(icon_path))
        
        self._menu = MenuApp(settings)
        self.setContextMenu(self._menu)
        #self.activated.connect(self.click_trap)



def read_user_settings():
    """
    Считывание пользовательских настроек.
    Если пользовательских настроек нет - создаем их из дефолтных
    """
    
    # путь до файла пользовательских настроек
    home_dir = os.path.expanduser('~')
    user_settings_dir = os.path.join(home_dir, USER_SETTINGS_DIR)
    user_settings_file = os.path.join(user_settings_dir, SETTINGS_FILE)

    # наличие каталога с пользовательскими настройками
    if os.path.exists(user_settings_dir) is False:
        # если файла настроек нет в текущем пользовательском каталооге - создаем его.
        default_settings_file = os.path.join(DEFAULT_SETTINGS_DIR, SETTINGS_FILE)
        

        os.mkdir(user_settings_dir)
        shutil.copy(default_settings_file, user_settings_file)

    with open(user_settings_file, 'r') as fp:
        data = json.load(fp)
        print(data)
        return data;


if __name__ == '__main__':

    DEFAULT_SETTINGS_DIR = '/usr/share/trad/'
    SETTINGS_FILE = 'settings.json'
    USER_SETTINGS_DIR = '.trad'
    ICON_FILE = 'trad-icon.png'

    settings = read_user_settings()
    
    icon_path = os.path.join(DEFAULT_SETTINGS_DIR, ICON_FILE)

    app = QtGui.QApplication([])
    tray = Tray(settings, icon_path)
    tray.show()
    app.exec_()
