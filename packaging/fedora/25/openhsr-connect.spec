%global srcname openhsr-connect

Name:           %{srcname}
#TODO: Version from outside
Version:        0.1.0.dev0
Release:        1%{?dist}
Summary:        Die offene HSR-Mapper Alternative

License:        GPLv3
URL:            https://www.openhsr.ch/connect
Source0:        openhsr-connect-%{version}.tar.gz

# build
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  python%{python3_pkgversion}-setuptools_scm

## test
#BuildRequires:  python%{python3_pkgversion}-pytest
#BuildRequires:  python%{python3_pkgversion}-msgpack >= 0.4.6

## docs
#%if 0%{?rhel}
## pyton3-sphinx packages are not available in epel
## so we use the old python2
#BuildRequires:  python-sphinx
#BuildRequires:  python-sphinx_rtd_theme
#%else
#BuildRequires:  python%{python3_pkgversion}-sphinx
#BuildRequires:  python%{python3_pkgversion}-sphinx_rtd_theme
#%endif

Requires:       python%{python3_pkgversion}-pysmb
Requires:       python%{python3_pkgversion}-click
Requires:       python%{python3_pkgversion}-ruamel-yaml
Requires:       python%{python3_pkgversion}-keyring
Requires:       python%{python3_pkgversion}-jsonschema
Requires:	python%{python3_pkgversion}
Requires:	cups


Requires(post): cups
Requires(preun): cups

%description
For more information, please checkout the Github page:
https://github.com/altcomphsr/connect

%prep
%setup -n %{srcname}-%{version}
rm -rf %{srcname}.egg-info

#%if 0%{?rhel}
## epel only has python2-sphinx and python2 has some problems
## with utf8 and it needs a patched docs until
## there is a python3 of sphinx
#%patch0 -p1
#%endif

%build
%py3_build
#%{__python3} setup.py build

## manpage
#%{__python3} setup.py build_usage
#%{__python3} setup.py build_api


#%if 0%{?rhel}
#make -C docs man
#%else
#make -C docs SPHINXBUILD=sphinx-build-3 man
#%endif

%install
%py3_install
#%{__python3} setup.py install -O1 --skip-build --root %{buildroot}


#%clean
#%{__rm} -rf %{buildroot}

#%py3_install
#install -D -m 0644 docs/_build/man/borg*.1* %{buildroot}%{_mandir}/man1/borg.1
%{__mkdir} -p %{buildroot}/usr/lib/cups/backend/ %{buildroot}/usr/share/ppd/openhsr-connect/
install openhsr_connect/resources/Generic-PostScript_Printer-Postscript.ppd %{buildroot}/usr/share/ppd/openhsr-connect/Generic-PostScript_Printer-Postscript.ppd
install -m 700 openhsr_connect/resources/openhsr-connect %{buildroot}/usr/lib/cups/backend/openhsr-connect

# TODO?
#%check
#PYTHONPATH=$(pwd) py.test-3 --pyargs borg.testsuite -vk "not test_non_ascii_acl and not test_fuse and not benchmark"

%post
if ! lpstat -a openhsr-connect > /dev/null 2>&1; then
    lpadmin -p openhsr-connect -E -v openhsr-connect:/tmp -P /usr/share/ppd/openhsr-connect/Generic-PostScript_Printer-Postscript.ppd
fi

%postun
if lpstat -a openhsr-connect > /dev/null 2>&1; then
    lpadmin -x openhsr-connect
fi

%files 
%license LICENSE.txt
#%doc README.md
#%{_mandir}/man1/*
%{python3_sitelib}/*
%{_bindir}/openhsr-connect
/usr/share/ppd/openhsr-connect/Generic-PostScript_Printer-Postscript.ppd
/usr/lib/cups/backend/openhsr-connect

%changelog
