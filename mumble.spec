Name:           mumble
Version:        1.2.18
Release:        1%{?dist}
Summary:        Voice chat suite aimed at gamers
Obsoletes:      mumble-protocol < 1.2.10-2
License:        BSD
URL:            http://www.mumble.info
Source0:        https://github.com/mumble-voip/mumble/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz 
Source1:        murmur.service
Source2:        %{name}.desktop
Patch1:         %{name}-1.2.4-celt_include_dir.patch
Patch2:         %{name}-fixspeechd.patch
# See https://fedoraproject.org/wiki/Packaging:CryptoPolicies
Patch3:         %{name}-FedoraCryptoPolicyCipherList.patch
# Disable d-bus rpc, this file is fixed upstream, remove on 1.3.0 release
Patch4:         %{name}-disablemurmurdbus.patch
# Murmur.ini modified upstream bug #1629 #1904
Patch5:         %{name}-FixNoBindAtBoot.patch
# Murmur will qFatal() if it does not have address to bind on start
Patch6:         %{name}-murmur_exit_on_no_bind.patch

BuildRequires:  qt4-devel, boost-devel
#BuildRequires:  ice-devel
BuildRequires:  alsa-lib-devel
BuildRequires:  pulseaudio-libs-devel, speex-devel
BuildRequires:  speech-dispatcher-devel, libogg-devel
BuildRequires:  libcap-devel, speexdsp-devel
BuildRequires:  desktop-file-utils, openssl-devel
BuildRequires:  libXevie-devel, celt071-devel
BuildRequires:  protobuf-compiler, avahi-compat-libdns_sd-devel
BuildRequires:  libsndfile-devel, protobuf-devel
BuildRequires:  opus-devel
#Due to naming issues, celt071 is required explicitly
Requires:       celt071

%description
Mumble provides low-latency, high-quality voice communication for gamers. 
It includes game linking, so voice from other players comes 
from the direction of their characters, and has echo 
cancellation so that the sound from your loudspeakers
won't be audible to other players.

%package -n murmur
Summary:    Mumble voice chat server
Provides:    %{name}-server = %{version}-%{release}
Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires: qt4-sqlite

%description -n murmur
Murmur(also called mumble-server) is part of the VoIP suite Mumble
primarily aimed at gamers. Murmur is the server component of the suite.

%package plugins
Summary:    Plugins for VoIP program Mumble
Requires:    %{name} = %{version}-%{release}

%description plugins
Mumble-plugins is part of VoIP suite Mumble primarily intended 
for gamers. This plugin allows game linking so the voice of 
players will come from the direction of their characters.

%package overlay
Summary:    Start games with the mumble overlay
Requires:    %{name} = %{version}-%{release}

%description overlay
Mumble-overlay is part of the Mumble VoIP suite aimed at gamers. If supported,
starting your game with this script will enable an ingame Mumble overlay.

%pre -n murmur
getent group mumble-server >/dev/null || groupadd -r mumble-server
getent passwd mumble-server >/dev/null || \
useradd -r -g mumble-server -d %{_localstatedir}/lib/%{name}-server/ -s /sbin/nologin \
-c "Mumble-server(murmur) user" mumble-server
exit 0

%prep
%setup -q
%patch1 -p1
%patch2 -p1 -F 2
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

%build
%{qmake_qt4} "CONFIG+=no-bundled-speex no-g15 \
no-embed-qt-translations no-update \
no-bundled-celt no-bundled-opus packaged \
no-ice" \
DEFINES+="PLUGIN_PATH=%{_libdir}/%{name}" \
DEFINES+="DEFAULT_SOUNDSYSTEM=PulseAudio" main.pro
make release %{?_smp_mflags}

%install
install -pD -m0755 release/%{name} %{buildroot}%{_bindir}/%{name}
install -pD -m0755 release/murmurd %{buildroot}%{_sbindir}/murmurd
ln -s murmurd %{buildroot}%{_sbindir}/%{name}-server

#translations
mkdir -p %{buildroot}/%{_datadir}/%{name}/translations
install -pm 644 src/%{name}/*.qm %{buildroot}/%{_datadir}/%{name}/translations

mkdir -p %{buildroot}%{_libdir}/%{name}/
install -p release/libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/
install -p release/plugins/*.so %{buildroot}%{_libdir}/%{name}/
ln -s libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/libmumble.so
ln -s libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/libmumble.so.1
ln -s libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/libmumble.so.1.2

#symlink for celt071
ln -s ../libcelt071.so.0.0.0 %{buildroot}%{_libdir}/%{name}/libcelt.so.0.7.0

mkdir -p %{buildroot}%{_sysconfdir}/murmur/
install -pD scripts/murmur.ini %{buildroot}%{_sysconfdir}/murmur/murmur.ini
ln -s /etc/murmur/murmur.ini %{buildroot}%{_sysconfdir}/%{name}-server.ini
install -pD -m0644 %{SOURCE1} %{buildroot}%{_unitdir}/murmur.service

mkdir -p %{buildroot}%{_datadir}/%{name}/
install -pD scripts/%{name}-overlay %{buildroot}%{_bindir}/%{name}-overlay

#man pages
mkdir -p %{buildroot}%{_mandir}/man1/
install -pD -m0644 man/murmurd.1 %{buildroot}%{_mandir}/man1/
install -pD -m0644 man/mumble* %{buildroot}%{_mandir}/man1/
install -pD -m0664 man/mumble-overlay.1 %{buildroot}%{_mandir}/man1/mumble-overlay.1

#icons
mkdir -p %{buildroot}%{_datadir}/icons/%{name}
install -pD -m0644 icons/%{name}.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

# install desktop file
desktop-file-install --dir=%{buildroot}%{_datadir}/applications \
%{SOURCE2}

#dir for mumble-server.sqlite
mkdir -p %{buildroot}%{_localstatedir}/lib/mumble-server/

%post
touch --no-create %{_datadir}/icons/hicolor &>/dev/null ||:

%postun 
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null ||:

%post -n murmur
%systemd_post murmur.service

%preun -n murmur
%systemd_preun murmur.service

%postun -n murmur
%systemd_postun_with_restart murmur.service

%files
%license LICENSE
%doc README README.Linux CHANGES
%doc scripts/weblist*
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%{_datadir}/applications/%{name}.desktop
%{_datadir}/mumble/
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/libcelt.so.0.7.0

%files -n murmur
%license LICENSE
%doc README README.Linux CHANGES
%attr(-,mumble-server,mumble-server) %{_sbindir}/murmurd
%{_unitdir}/murmur.service
%{_sbindir}/%{name}-server
%config(noreplace) %attr(664,mumble-server,mumble-server) %{_sysconfdir}/murmur/murmur.ini
%config(noreplace) %{_sysconfdir}/%{name}-server.ini
%{_mandir}/man1/murmurd.1*
%dir %attr(-,mumble-server,mumble-server) %{_localstatedir}/lib/mumble-server/

%files plugins
%{_libdir}/%{name}/libmanual.so
%{_libdir}/%{name}/liblink.so

%files overlay
%{_bindir}/%{name}-overlay
%{_libdir}/%{name}/lib%{name}*
%{_mandir}/man1/mumble-overlay.1*

%changelog
* Thu Dec 15 2016 Filipe Rosset <rosset.filipe@gmail.com> - 1.2.18-1
- Rebuilt for new upstream release 1.2.18, fixes rhbz #1293181

* Sat Nov 19 2016 Orion Poplawski <orion@cora.nwra.com> - 1.2.11-4
- Rebuild for protobuf 3.1.0

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.11-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec 7 2015 John Popplewell <johnhatestrash@gmail.com> - 1.2.11-2
- Removed perl dependency and all deprecated d-bus rpc support

* Sun Dec 6 2015 John Popplewell <johnhatestrash@gmail.com> - 1.2.11-1
- Update to 1.2.11
- Added mumble-FixNoBindAtBoot.patch mumble-murmur_exit_on_no_bind.patch

* Wed Nov 25 2015 John Popplewell <johnhatestrash@gmail.com> - 1.2.10-4
- Hardened murmur.service
- Added patch to disable murmur.ini d-bus rpc - remove on 1.3.0

* Wed Nov 25 2015 John Popplewell <johnhatestrash@gmail.com> - 1.2.10-3
- Added ppc support
- Marked LICENSE with license tag
- Added patch to modify murmur.ini with PROFILE=SYSTEM sslCipher= setting

* Tue Nov 24 2015 John Popplewell <johnhatestrash@gmail.com> - 1.2.10-2
- Removed protocol subpkg, added Obsoletes mumble-protocol < 1.2.10-2
- Made recommended review changes (qmake_qt4, added parallel make, qt4-devel in favor of qt-devel)

* Tue Nov 24 2015 John Popplewell <johnhatestrash@gmail.com> - 1.2.10-1
- Update to 1.2.10
- Drop ice

* Tue Jan 13 2015 Carlos O'Donell <codonell@redhat.com> - 1.2.6-5
- Rebuilt against new ice-devel.

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 23 2014 Petr Machata <pmachata@redhat.com> - 1.2.6-2
- Rebuild for boost 1.55.0

* Sat May 17 2014 Christian Krause <chkr@fedoraproject.org> - 1.2.6-1
- Update 1.2.6
- Update fixes CVE-2014-3755 (BZ 1098231) and CVE-2014-3756 (BZ 1098233)

* Fri Apr 25 2014 Christian Krause <chkr@fedoraproject.org> - 1.2.5-1
- Update 1.2.5 (BZ 1062209)
- Update fixes CVE-2014-0044 (BZ 1061857) and CVE-2014-0045 (BZ 1061858)
- Add patch to fix an compile error with g++ 4.9.0
- Remove upstreamed patch for CVE-2012-0863

* Tue Aug 27 2013 Christian Krause <chkr@fedoraproject.org> - 1.2.4-1
- Update 1.2.4 (BZ 976001)
- New systemd-rpm macros (BZ 850218)
- Cleanup

* Mon Aug 19 2013 Peter Robinson <pbrobinson@fedoraproject.org> 1.2.3-16
- Fix FTBFS due to speechd
- Drop alsa-oss support

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.3-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 30 2013 Petr Machata <pmachata@redhat.com> - 1.2.3-14
- Rebuild for boost 1.54.0

* Wed Apr 03 2013 Christian Krause <chkr@fedoraproject.org> - 1.2.3-13
- Rebuild against new ice package
- Updated Ice version in patch0

* Sun Mar 17 2013 Christian Krause <chkr@fedoraproject.org> - 1.2.3-12
- Rebuild against new protobuf package

* Wed Feb 06 2013 Christian Krause <chkr@fedoraproject.org> - 1.2.3-11
- Rebuild against new ice package
- Updated Ice version in patch0
- Use new systemd-rpm macros (BZ 850218)

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.3-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu May 31 2012 Christian Krause <chkr@fedoraproject.org> - 1.2.3-9
- Fix startup issues of murmurd (BZ 711711, BZ 770469, BZ 771423)
- Fix migration to systemd
  http://fedoraproject.org/wiki/Packaging:ScriptletSnippets#Systemd
- Fix directory ownership of %%{_libdir}/mumble and %%{_datadir}/mumble*
  (BZ 744886)
- Add upstream patch for CVE-2012-0863 (BZ 791058)
- Fix broken logrotate config file (BZ 730129)
- Add dependency for qt4-sqlite (BZ 660221)
- Remove /sbin/ldconfig from %%post(un) since mumble does not
  contain any libraries in %%{_libdir}
- Some minor cleanup

* Wed Apr 18 2012 Jon Ciesla <limburgher@gmail.com> - 1.2.3-8
- Migrate to systemd, BZ 790040.

* Fri Mar 16 2012 Tom Callaway <spot@fedoraproject.org> - 1.2.3-7
- rebuild against fixed ice

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Nov 10 2011 Andreas Osowski <th0br0@mkdir.name> - 1.2.3-5
- Updated Ice version in patch0
- Added new patch to build against celt071 includes thanks to Florent Le Coz

* Thu Nov 10 2011 Andreas Osowski <th0br0@mkdir.name> - 1.2.3-4
- rebuilt for protobuf update

* Mon Sep 12 2011 Andreas Osowski <th0br0@mkdir.name> - 1.2.3-3
- Rebuild for newer protobuf

* Tue May 17 2011 Andreas Osowski <th0br0@mkdir.name> - 1.2.3-2
- Added celt071 functionality
- Fixed the qmake args

* Wed Mar 30 2011 Andreas Osowski <th0br0@mkdir.name> - 1.2.3-1
- Update to 1.2.3
- Fixes vulnerability #610845
- Added patch to make it compile with Ice 3.4.0
- Added tmpfile.d config file for murmur

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.2-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Aug 25 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-10
- Actually removed the requirement for redhat-lsb

* Tue Aug 03 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-9
- Removed redhat-lsb from Requires for murmur
- Updated initscript for murmur

* Sun May 16 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-8
- Rebuild for protobuf ABI change
- Added redhat-lsb to the Requires for murmur

* Sun May  2 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-7
- Fixed murmur's init script

* Sun Apr 18 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-6
- Fix for missing dbus-qt-devel on >F12

* Sun Apr 18 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-5
- Merged Mary Ellen Foster's changelog entry

* Tue Mar 30 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-4
- Marked the files in /etc as config entries

* Tue Mar 23 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-3
- Added desktop file for mumble11x

* Mon Feb 22 2010 Julian Golderer <j.golderer@novij.at> - 1.2.2-2
- Added mumble11x
- Added svg icons
- Added language files

* Sun Feb 21 2010 Andreas Osowski <th0br0@mkdir.name> - 1.2.2-1
- Update to 1.2.2



