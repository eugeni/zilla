PACKAGE = zilla
VERSION = 0.0.1

version:
	echo "version='$(VERSION)'" > version.py

install:
	mkdir -p $(RPM_BUILD_ROOT)/usr/share/zilla
	mkdir -p $(RPM_BUILD_ROOT)/usr/share/icons
	mkdir -p $(RPM_BUILD_ROOT)/usr/bin
	install -m755 zilla.py $(RPM_BUILD_ROOT)/usr/bin/zilla
	install -m644 zilla.png $(RPM_BUILD_ROOT)/usr/share/icons
	# locale
	$(MAKE) -C po $@
	# desktop
	mkdir -p $(RPM_BUILD_ROOT)/usr/share/applications/
	install -m644 zilla.desktop $(RPM_BUILD_ROOT)/usr/share/applications/

cleandist:
	rm -rf $(PACKAGE)-$(VERSION) $(PACKAGE)-$(VERSION).tar.bz2

tar:
	tar cfj $(PACKAGE)-$(VERSION).tar.bz2 $(PACKAGE)-$(VERSION)
	rm -rf $(PACKAGE)-$(VERSION)

gitdist: cleandist
	git archive --prefix $(PACKAGE)-$(VERSION)/ HEAD | bzip2 -9 > $(PACKAGE)-$(VERSION).tar.bz2
