%global srcname jsonschema

Name:           python3-%{srcname}
#TODO: Version from outside
Version:        2.6.0
Release:        1%{?dist}
Summary:        An implementation of JSON Schema validation for Python3 (library only)

License:        mit
URL:            https://github.com/Julian/jsonschema
Source0:        jsonschema-%{version}.tar.gz

# build
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  python%{python3_pkgversion}-setuptools_scm

Requires:	python%{python3_pkgversion}
Requires:       python%{python3_pkgversion}-pyasn1


%description
jsonschema is an implementation of JSON Schema for Python (supporting 2.7+ including Python 3).
NOTE: This package provides the python3-libraries only, and not an executable. If you want a
executable version, please use the python-jsonschema package.

%prep
%setup -n %{srcname}-%{version}
rm -rf %{srcname}.egg-info

%build
%py3_build

%install
%py3_install

# We only want the library, python-jsonschema already provides an executable
rm %{buildroot}%{_bindir}/jsonschema

%files 
%{python3_sitelib}/*
%changelog
