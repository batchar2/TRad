#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json


from PyQt4 import QtGui, QtCore



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



class MenuApp(QtGui.QMenu):
    
    _active_station = None

    def __init__(self, settings = [], parent=None):
        
        super(MenuApp, self).__init__("TrayRadio", parent)

        icon = QtGui.QIcon.fromTheme("edit-copy")
        

        self._station_play_control = QtGui.QAction(u'Не выбранно', self)
        self.addAction(self._station_play_control)
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
        

    def _change_station(self):
        name = self._active_station['name']
        self._station_play_control.setText(name)


    def _set_station(self, station):
        self._active_station = station
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
