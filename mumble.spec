Name:		mumble
Version:	1.1.8
Release:	16%{?dist}
Summary:	Voice chat software primarily intended for use while gaming

Group:		Applications/Internet
License:	BSD
URL:		http://%{name}.sourceforge.net/
Source0:	http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
Source1:	murmur.init
Source2:	%{name}.desktop
Source3:	%{name}-overlay.desktop
#fixes compile error on f10 and above
Patch0:		compile-fix.patch
#modify linker to add extra needed libraries (F13+)
Patch1:		mumble-add-needed.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	qt-devel, boost-devel, ice-devel
BuildRequires:	alsa-lib-devel, alsa-oss-devel
BuildRequires:	pulseaudio-libs-devel, speex-devel
BuildRequires:	speech-dispatcher-devel, libogg-devel
BuildRequires:	libcap-devel
BuildRequires:	desktop-file-utils, openssl-devel

# Due to missing ice-devel on ppc64 arch
ExcludeArch: ppc64

%description
Low-latency, high-quality voice communication for gamers. 
Includes game linking, so voice from other players comes 
from the direction of their characters, and has echo 
cancellation so the sound from your loudspeakers
won't be audible to other players.

%package -n murmur
Summary:	Mumble voice chat server
Group:		System Environment/Daemons
Provides:	%{name}-server = %{version}-%{release}

Requires(pre): shadow-utils
Requires(post): chkconfig
Requires(preun): chkconfig, initscripts
Requires(postun): initscripts

%description -n murmur
Murmur(also called mumble-server) is part of VoIP suite Mumble
primarily intended for gamers. Murmur is server part of suite.

%package plugins
Summary:	Plugins for VoIP program Mumble
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description plugins
Mumble-plugins is part of VoIP suite Mumble primarily intended 
for gamers. This plugin allows game linking so the voice of 
players will come from the direction of their characters.

%package overlay
Summary:	Start Mumble with overlay
Group:		Applications/Internet
Requires:	%{name} = %{version}-%{release}

%description overlay
Mumble-overlay is part of VoIP suite Mumble primarily intended
for gamers. Mumble-overlay shows players in current channel and linked channels
in game so you don't need to quit the game to see who is in your channel.

%package protocol
Summary:	Package to support mumble protocol
Group:		Applications/Internet
Requires:	%{name} = %{version}-%{release}	
Requires:	kde-filesystem

%description protocol
Low-latency, high-quality voice communication for gamers.
Includes game linking, so voice from other players comes
from the direction of their characters, and has echo
cancellation so the sound from your loudspeakers
won't be audible to other players.

%pre -n murmur
getent group mumble-server >/dev/null || groupadd -r mumble-server
getent passwd mumble-server >/dev/null || \
useradd -r -g mumble-server -d %{_localstatedir}/lib/%{name}-server/ -s /sbin/nologin \
-c "Mumble-server(murmur) user" mumble-server
exit 0

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
qmake-qt4 "CONFIG+=no-bundled-speex no-g15 \
no-embed-qt-translations no-update \
QMAKE_CFLAGS_RELEASE=%{optflags} \
QMAKE_CXXFLAGS_RELEASE=%{optflags} \
DEFINES+=PLUGIN_PATH=%{_libdir}/%{name} \
DEFINES+=DEFAULT_SOUNDSYSTEM=PulseAudio" main.pro
make %{?_smp_mflags}

%install
rm -rf %{buildroot}

install -pD -m0755 release/%{name} %{buildroot}%{_bindir}/%{name}
install -pD -m0755 release/murmurd %{buildroot}%{_sbindir}/murmurd
ln -s murmurd %{buildroot}%{_sbindir}/%{name}-server
#ln -s ../sbin/murmurd %{buildroot}%{_sbindir}/murmur 

mkdir -p %{buildroot}%{_libdir}/%{name}/
#install -d %{buildroot}%{_libdir}/%{name}/
#install -p release/libmumble.so* %{buildroot}%{_libdir}/
# obviusly install doesn't preserve symlinks
# mumble will complain loudly if it cant find libmumble.so inside /usr/lib/
install -p release/libmumble.so.%{version} %{buildroot}%{_libdir}/
ln -s %{_libdir}/libmumble.so.%{version} %{buildroot}%{_libdir}/libmumble.so
ln -s %{_libdir}/libmumble.so.%{version} %{buildroot}%{_libdir}/libmumble.so.1
ln -s %{_libdir}/libmumble.so.%{version} %{buildroot}%{_libdir}/libmumble.so.1.1
install -p release/plugins/*.so %{buildroot}%{_libdir}/%{name}/
ln -s %{_libdir}/libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/libmumble.so
ln -s %{_libdir}/libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/libmumble.so.1
ln -s %{_libdir}/libmumble.so.%{version} %{buildroot}%{_libdir}/%{name}/libmumble.so.1.1

mkdir -p %{buildroot}%{_sysconfdir}/murmur/
install -pD scripts/murmur.ini.system %{buildroot}%{_sysconfdir}/murmur/murmur.ini
ln -s ../etc/murmur/murmur.ini %{buildroot}%{_sysconfdir}/%{name}-server.ini
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
install -pD -m0644 icons/%{name}.16x16.png %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
install -pD -m0644 icons/%{name}.32x32.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
install -pD -m0644 icons/%{name}.48x48.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
install -pD -m0644 icons/%{name}.64x64.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/%{name}.png

#logrotate
install -pD scripts/murmur.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/murmur

# install desktop file
desktop-file-install --dir=%{buildroot}%{_datadir}/applications \
%{SOURCE2}

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
mkdir -p %{buildroot}%{_localstatedir}/run/mumble-server/

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
%doc scripts/*.pl scripts/*%{name}-policy*
%doc scripts/*php scripts/qt.conf
%{_libdir}/libmumble.so*
%{_libdir}/%{name}/libmumble.so*
%{_bindir}/%{name}
#%attr(664,root,root) %{_datadir}/%{name}/*
%{_mandir}/man1/%{name}*
#%{_mandir}/man1/%{name}-overlay.1
%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
%{_datadir}/icons/hicolor/64x64/apps/%{name}.png
%{_datadir}/applications/%{name}.desktop
#%{_datadir}/hal/fdi/policy/20thirdparty/11-input-mumble-policy.fdi

%files -n murmur
%defattr(-,root,root,-)
%doc README README.Linux LICENSE CHANGES
#%attr(-,mumble-server,mumble-server) %{_sbindir}/murmur
%attr(-,mumble-server,mumble-server) %{_sbindir}/murmurd
%attr(-,mumble-server,mumble-server) %{_initrddir}/murmur
%{_sbindir}/%{name}-server
%config(noreplace) %attr(664,mumble-server,mumble-server) %{_sysconfdir}/murmur/murmur.ini
%config(noreplace) %attr(664,mumble-server,mumble-server) %{_sysconfdir}/mumble-server.ini
%{_mandir}/man1/murmurd.1*
%attr(664,root,root) %{_sysconfdir}/logrotate.d/murmur
%{_sysconfdir}/dbus-1/system.d/murmur.conf
%dir %attr(-,mumble-server,mumble-server) %{_localstatedir}/lib/mumble-server/
%dir %attr(-,mumble-server,mumble-server) %{_localstatedir}/log/mumble-server/
%dir %attr(-,mumble-server,mumble-server) %{_localstatedir}/run/mumble-server/

%files plugins
%defattr(-,root,root,-)
%{_libdir}/%{name}

%files overlay
%defattr(-,root,root,-)
%{_bindir}/%{name}-overlay
#%{_datadir}/applications/%{name}-overlay.desktop

%files protocol
%defattr(-,root,root,-)
%{_datadir}/kde4/services/mumble.protocol

%changelog
* Tue Mar 22 2010 Mary Ellen Foster <mefoster@gmail.com> - 1.1.8-16
- Rebuild with new ice-3.4.0
- Fix UTF-8 characters in changelog
- Add --add-needed to link line so that it finds librt

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

