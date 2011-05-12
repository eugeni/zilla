Summary:	Zilla is a desktop-based bugzilla client with smart search
Name:		zilla
Version:	0.0.1
Release:	%mkrel 1
Source0:	%name-%version.tar.bz2
License:	GPLv2
Group:		Networking/Other
Url:		https://github.com/eugeni/zilla
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: python-devel
BuildArch: noarch
Requires:  python
Requires:  pygtk2.0

%description
Zilla is a desktop-based bugzilla client with smart search capabilities.

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std
%find_lang %name


%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(-,root,root) 
%doc README
%_bindir/zilla
%_datadir/icons/zilla.png
%_datadir/applications/zilla.desktop
