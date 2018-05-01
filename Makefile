all: create_deb

create_deb:
	mkdir -p /tmp/trad-deb/TRAD/DEBIAN
	echo "" > /tmp/trad-deb/TRAD/DEBIAN/changelog

	echo "Package: trad" > /tmp/trad-deb/TRAD/DEBIAN/control
	echo "Version: 0.3" >> /tmp/trad-deb/TRAD/DEBIAN/control
	echo "Provides: trad" >> /tmp/trad-deb/TRAD/DEBIAN/control
	echo "Architecture: all" >> /tmp/trad-deb/TRAD/DEBIAN/control
	echo "Section: sound" >> /tmp/trad-deb/TRAD/DEBIAN/control
	echo "Description: test-packet" >> /tmp/trad-deb/TRAD/DEBIAN/control
	echo "Installed-Size: 3" >> /tmp/trad-deb/TRAD/DEBIAN/control
	echo "Priority: optional" >> /tmp/trad-deb/TRAD/DEBIAN/control
	echo "Depends: dpkg, python2.7, gstreamer1.0-alsa, \
			gstreamer1.0-plugins-base, gstreamer1.0-plugins-good" >> /tmp/trad-deb/TRAD/DEBIAN/control
 	
	echo "/usr/share/trad" > /tmp/trad-deb/TRAD/DEBIAN/dirs
	echo "" > /tmp/trad-deb/TRAD/DEBIAN/md5sum
	echo "" > /tmp/trad-deb/TRAD/DEBIAN/rules
	
	touch /tmp/trad-deb/TRAD/DEBIAN/postrm
	chmod +x /tmp/trad-deb/TRAD/DEBIAN/postrm

	touch /tmp/trad-deb/TRAD/DEBIAN/postinst
	chmod +x /tmp/trad-deb/TRAD/DEBIAN/postinst

	mkdir -p /tmp/trad-deb/TRAD/usr/bin
	mkdir -p /tmp/trad-deb/TRAD/usr/share/trad

	cp -v data/settings.json /tmp/trad-deb/TRAD/usr/share/trad
	cp -v data/trad-icon.png /tmp/trad-deb/TRAD/usr/share/trad
	cp -v src/trad.py /tmp/trad-deb/TRAD/usr/bin/trad
	
	current_path=`pwd`
	dpkg-deb -b /tmp/trad-deb/TRAD TRad.deb

	echo "Success!"