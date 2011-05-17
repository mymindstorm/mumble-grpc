Name:		mumble
Version:	1.2.3
Release:	2%{?dist}
Summary:	Voice chat suite aimed at gamers

Group:		Applications/Internet
License:	BSD
URL:		http://%{name}.sourceforge.net/
Source0:	http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
Source1:	murmur.init
Source2:	%{name}.desktop
Source3:	%{name}11x.desktop
Source4:	%{name}-overlay.desktop
Source5:	murmur-tmpfiles.conf
Patch0:		%{name}-%{version}-slice2cpp.patch
#fixes compile error on f10 and above
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	qt-devel, boost-devel, ice-devel
BuildRequires:	alsa-lib-devel, alsa-oss-devel
BuildRequires:	pulseaudio-libs-devel, speex-devel
BuildRequires:	speech-dispatcher-devel, libogg-devel
BuildRequires:	libcap-devel
BuildRequires:	desktop-file-utils, openssl-devel
BuildRequires:	libXevie-devel, celt-devel
BuildRequires:	protobuf-compiler, avahi-compat-libdns_sd-devel
BuildRequires:	libsndfile-devel, protobuf-devel
Requires:	celt071

# Due to missing ice on ppc64
ExcludeArch: ppc64

%description
Mumble provides low-latency, high-quality voice communication for gamers. 
It includes game linking, so voice from other players comes 
from the direction of their characters, and has echo 
cancellation so that the sound from your loudspeakers
won't be audible to other players.

%package -n murmur
Summary:	Mumble voice chat server
Group:		System Environment/Daemons
Provides:	%{name}-server = %{version}-%{release}

Requires(pre): shadow-utils
Requires(post): chkconfig
Requires(preun): chkconfig
Requires: initscripts

%description -n murmur
Murmur(also called mumble-server) is part of the VoIP suite Mumble
primarily aimed at gamers. Murmur is the server component of the suite.

%package plugins
Summary:	Plugins for VoIP program Mumble
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description plugins
Mumble-plugins is part of VoIP suite Mumble primarily intended 
for gamers. This plugin allows game linking so the voice of 
players will come from the direction of their characters.

%package overlay
Summary:	Start games with the mumble overlay
Group:		Applications/Internet
Requires:	%{name} = %{version}-%{release}

%description overlay
Mumble-overlay is part of the Mumble VoIP suite aimed at gamers. If supported,
starting your game with this script will enable an ingame Mumble overlay.

%package protocol
Summary:	Support for the mumble protocol
Group:		Applications/Internet
Requires:	%{name} = %{version}-%{release}	
Requires:	kde-filesystem

%description protocol
Mumble is a Low-latency, high-quality voice communication suite
for gamers. It includes game linking, so voice from other players
comes from the direction of their characters, and echo cancellation
so that the sound from your loudspeakers won't be audible to other players.

%pre -n murmur
getent group mumble-server >/dev/null || groupadd -r mumble-server
getent passwd mumble-server >/dev/null || \
useradd -r -g mumble-server -d %{_localstatedir}/lib/%{name}-server/ -s /sbin/nologin \
-c "Mumble-server(murmur) user" mumble-server
exit 0

%prep
%setup -q
%patch0 -p1

%build
%{_qt4_qmake} "CONFIG+=no-bundled-speex no-g15 \
no-embed-qt-translations no-update \
no-bundled-celt" \
QMAKE_CFLAGS_RELEASE="%{optflags}" \
QMAKE_CXXFLAGS_RELEASE="%{optflags}" \
DEFINES+="PLUGIN_PATH=%{_libdir}/%{name}" \
DEFINES+="DEFAULT_SOUNDSYSTEM=PulseAudio" main.pro
make 
#%{?_smp_mflags}

%install
rm -rf %{buildroot}

install -pD -m0755 release/%{name} %{buildroot}%{_bindir}/%{name}
install -pD -m0755 release/%{name}11x %{buildroot}%{_bindir}/%{name}11x
install -pD -m0755 release/murmurd %{buildroot}%{_sbindir}/murmurd
ln -s murmurd %{buildroot}%{_sbindir}/%{name}-server
#ln -s ../sbin/murmurd %{buildroot}%{_sbindir}/murmur 

#translations
mkdir -p %{buildroot}/%{_datadir}/%{name}/translations
mkdir -p %{buildroot}/%{_datadir}/%{name}11x/translations
install -pm 644 src/%{name}/*.qm %{buildroot}/%{_datadir}/%{name}/translations
install -pm 644 src/%{name}11x/*.qm %{buildroot}/%{_datadir}/%{name}11x/translations


mkdir -p %{buildroot}%{_libdir}/%{name}/
#install -d %{buildroot}%{_libdir}/%{name}/
#install -p release/libmumble.so* %{buildroot}%{_libdir}/
# obviusly install doesn't preserve symlinks
# mumble will complain loudly if it cant find libmumble.so inside /usr/lib/
install -p release/libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/
install -p release/plugins/*.so %{buildroot}%{_libdir}/%{name}/
ln -s libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/libmumble.so
ln -s libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/libmumble.so.1
ln -s libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/libmumble.so.1.2

#symlink for celt071
ln -s ../libcelt071.so.0.0.0 %{buildroot}%{_libdir}/%{name}/libcelt.so.0.7.0

mkdir -p %{buildroot}%{_sysconfdir}/murmur/
install -pD scripts/murmur.ini.system %{buildroot}%{_sysconfdir}/murmur/murmur.ini
ln -s /etc/murmur/murmur.ini %{buildroot}%{_sysconfdir}/%{name}-server.ini
install -pD -m0755 %{SOURCE1} %{buildroot}%{_initrddir}/murmur

mkdir -p %{buildroot}%{_datadir}/%{name}/
install -pD scripts/%{name}-overlay %{buildroot}%{_bindir}/%{name}-overlay

#man pages
mkdir -p %{buildroot}%{_mandir}/man1/
install -pD -m0644 man/murmurd.1 %{buildroot}%{_mandir}/man1/
install -pD -m0644 man/mumble* %{buildroot}%{_mandir}/man1/
#install -pD -m0664 man/mumble-overlay.1 %{buildroot}%{_mandir}/man1/mumble-overlay.1

#icons
mkdir -p %{buildroot}%{_datadir}/icons/%{name}
install -pD -m0644 icons/%{name}.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
install -pD -m0644 src/mumble11x/resources/%{name}.16x16.png %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
install -pD -m0644 src/mumble11x/resources/%{name}.32x32.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
install -pD -m0644 src/mumble11x/resources/%{name}.48x48.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
install -pD -m0644 src/mumble11x/resources/%{name}.64x64.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/%{name}.png

#logrotate
install -pD scripts/murmur.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/murmur

# install desktop file
desktop-file-install --dir=%{buildroot}%{_datadir}/applications \
%{SOURCE2}

#install desktop file for mumble11x
desktop-file-install --dir=%{buildroot}%{_datadir}/applications \
%{SOURCE3}

#install desktop file for mumble-overlay
#desktop-file-install --dir=%{buildroot}%{_datadir}/applications \
#%{SOURCE3}

# install the mumble protocol
install -pD -m0644 scripts/%{name}.protocol %{buildroot}%{_datadir}/kde4/services/%{name}.protocol

# murmur.conf
install -pD -m0644 scripts/murmur.conf %{buildroot}%{_sysconfdir}/dbus-1/system.d/murmur.conf

#dir for mumble-server.sqlite
mkdir -p %{buildroot}%{_localstatedir}/lib/mumble-server/

#log dir
mkdir -p %{buildroot}%{_localstatedir}/log/mumble-server/

#pid dir
mkdir -p %{buildroot}%{_localstatedir}/run/
install -d -m 0710 %{buildroot}%{_localstatedir}/run/mumble-server/

%if 0%{?fedora} >= 15
#tmpfiles.d
mkdir -p %{buildroot}%{_sysconfdir}/tmpfiles.d
install -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/tmpfiles.d/%{name}.conf
%endif

%post
/sbin/ldconfig
touch --no-create %{_datadir}/icons/hicolor &>/dev/null ||:

%postun 
/sbin/ldconfig
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%postun -n murmur
if [ $1 -ge 1 ] ; then
    /sbin/service murmur condrestart >/dev/null 2>&1 || :
fi

%posttrans 
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null ||: 


%clean
rm -rf %{buildroot}

%preun -n murmur
if [ $1 = 0 ] ; then
	/sbin/service murmur stop > /dev/null 2>&1 || :
	/sbin/chkconfig --del murmur || :
fi

%post -n murmur
/sbin/chkconfig --add murmur || :


%files
%defattr(-,root,root,-)
%doc README README.Linux LICENSE CHANGES
%doc scripts/weblist*
%{_bindir}/%{name}
%{_bindir}/%{name}11x
#%attr(664,root,root) %{_datadir}/%{name}/*
%{_mandir}/man1/%{name}*
#%{_mandir}/man1/%{name}-overlay.1
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
%{_datadir}/icons/hicolor/64x64/apps/%{name}.png
%{_datadir}/applications/%{name}.desktop
%{_datadir}/applications/%{name}11x.desktop
#%{_datadir}/hal/fdi/policy/20thirdparty/11-input-mumble-policy.fdi
%{_datadir}/%{name}/translations/%{name}_*.qm
%{_datadir}/%{name}11x/translations/%{name}_*.qm
%{_libdir}/%{name}/libcelt.so.0.7.0

%files -n murmur
%defattr(-,root,root,-)
%doc README README.Linux LICENSE CHANGES
%doc scripts/murmur.pl scripts/murmur-user-wrapper
#%attr(-,mumble-server,mumble-server) %{_sbindir}/murmur
%attr(-,mumble-server,mumble-server) %{_sbindir}/murmurd
%{_initrddir}/murmur
%{_sbindir}/%{name}-server
%config(noreplace) %attr(664,mumble-server,mumble-server) %{_sysconfdir}/murmur/murmur.ini
%config(noreplace) %attr(664,mumble-server,mumble-server) %{_sysconfdir}/mumble-server.ini
%{_mandir}/man1/murmurd.1*
%attr(664,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/murmur
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/murmur.conf
%dir %attr(-,mumble-server,mumble-server) %{_localstatedir}/lib/mumble-server/
%dir %attr(-,mumble-server,mumble-server) %{_localstatedir}/log/mumble-server/
%ghost %dir %{_localstatedir}/lib/mumble-server/
%ghost %dir %{_localstatedir}/log/mumble-server/
%if 0%{?fedora} >= 15
%dir %{_localstatedir}/run/mumble-server/
%config(noreplace) %{_sysconfdir}/tmpfiles.d/%{name}.conf
%else
%ghost %dir %{_localstatedir}/run/mumble-server/
%endif

%files plugins
%defattr(-,root,root,-)
%{_libdir}/%{name}/libmanual.so
%{_libdir}/%{name}/liblink.so

%files overlay
%defattr(-,root,root,-)
%{_bindir}/%{name}-overlay
%{_libdir}/%{name}/lib%{name}*

%files protocol
%defattr(-,root,root,-)
%{_datadir}/kde4/services/mumble.protocol

%changelog
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

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1.1.8-15
- rebuilt with new openssl

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.8-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue May 19 2009 Igor Jurišković <juriskovic.igor@gmail.com> 1.1.8-13
- Fixed mumble-overlay error.
- Fixed some scriptlets and requirements.

* Mon May 18 2009 Igor Jurišković <juriskovic.igor@gmail.com> 1.1.8-12
- Fixed mumble-server user directory.
- Added condrestart at postun.

* Sun May 17 2009 Igor Jurišković <juriskovic.igor@gmail.com> 1.1.8-11
- Changed home dir of mumble-server user.
- Added deps for murmur.
- Included patch to successfully compile mumble on F10 and F11.
- Murmur no longer starts at levels 345.
- Init script no longer calls success twice when you stop it.

* Fri May 15 2009 Igor Jurišković <juriskovic.igor@gmail.com> 1.1.8-10
- Added shadow-utils as pre requirement.
- Added kde-filesystem as requirement.
- Added parallel make
- Removed attr(....) on symlink.
- Man pages are now installed under man1.
- Fixed permissions on some files.
- Fixed inconsistent command.
- Fixed GTK cache update.
- Fixed a lot of other errors pointed at review request(497441)

* Mon May 4 2009 Igor Jurišković <juriskovic.igor@gmail.com> 1.1.8-9
- Fixed symbolic link error.

* Wed Apr 29 2009 Igor Jurišković <juriskovic.igor@gmail.com> 1.1.8-8
- Excluded ppc64 arch due to missing ice-devel dependency.

* Tue Apr 28 2009 Igor Jurišković <juriskovic.igor@gmail.com> 1.1.8-7
- Changed user murmur to mumble-server to avoid need of modifying ini and conf files
- Removed murmurd symlink.

* Mon Apr 27 2009 Igor Jurišković <juriskovic.igor@gmail.com> 1.1.8-6
- Added optimization flags.
- Fixed symlink error while installing binary mumble rpm.
- Installed mumble.logrotate to right location.
- Murmur started as daemon will start as user:group -> murmur:murmur
- Added mumble protocol.
- Added murmur.conf.
- Added no-embed-qt-translations to get rid of embedded qt translation probs.
- Added no-update.
- Added plugin path.
- Default sound system is now PulseAudio.
- Fixed dbus and sqlite dependency problems.
- murmur.ini is now based on murmur.ini.system

* Mon Apr 27 2009 Igor Jurišković <juriskovic.igor@gmail.com> 1.1.8-5
- Added mumble-overlay as subpackage.
- Plugins are now subpackage.
- Fixed a lot of small errors.

* Mon Apr 27 2009 Igor Jurišković <juriskovic.igor@gmail.com> 1.1.8-4
- Fixed many errors in murmur.init pointed at review request(497441).
- Fixed Requires in murmur subpackage.

* Sun Apr 26 2009 Igor Jurišković <juriskovic.igor@gmail.com> 1.1.8-3
- Added desktop file for mumble(client).
- Added man pages for mumble and murmur.
- Added icons.
- Scripts are stored to /usr/share/mumble(non-executable).

* Sat Apr 25 2009 Igor Jurišković <juriskovic.igor@gmail.com> 1.1.8-2
- Changed murmur.init lockfile to /var/lock/subsys/murmur.
- Fixed permissions on murmur.ini and mumble-server.ini.
- Added noreplace to prevent file deleting on new installation.
- Added new user and group both called murmur.
- Mumble is now built against speex from repositories.
- Fixed a lot of small errors pointed at package review.

* Wed Apr 23 2009 Igor Jurišković <juriskovic.igor@gmail.com> 1.1.8-1
- Initial revision.
