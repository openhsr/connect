%global srcname pysmb

Name:           python3-%{srcname}
#TODO: Version from outside
Version:        1.1.19
Release:        1%{?dist}
Summary:        Experimental SMB/CIFS library written in Python.

License:        zlib/libpng
URL:            https://github.com/miketeo/pysmb
Source0:        pysmb-%{version}.tar.gz

# build
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  python%{python3_pkgversion}-setuptools_scm

Requires:	python%{python3_pkgversion}
Requires:       python%{python3_pkgversion}-pyasn1


%description
pysmb is an experimental SMB/CIFS library written in Python. It implements the client-side SMB/CIFS protocol (SMB1 and SMB2) which allows your Python application to access and transfer files to/from SMB/CIFS shared folders like your Windows file sharing and Samba folders.

%prep
%setup -n %{srcname}-%{version}
rm -rf %{srcname}.egg-info

%build
%py3_build

%install
%py3_install

%files 
%license LICENSE
%{python3_sitelib}/*
%changelog
