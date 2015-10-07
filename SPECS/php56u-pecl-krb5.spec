%global pecl_name krb5
%global real_name php-pecl-krb5
%global php_base  php56u
%global ini_name  40-%{pecl_name}.ini

# RPM 4.8
%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_setup}
# RPM 4.9
%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}%{php_extdir}/.*\\.so$


Summary:       Kerberos authentification extension
Name:          %{php_base}-pecl-krb5
Version:       1.0.0
Release:       1.ius%{?dist}
License:       BSD
Group:         Development/Languages
URL:           http://pecl.php.net/package/%{pecl_name}
Source0:       http://pecl.php.net/get/%{pecl_name}-%{version}.tgz
BuildRequires: %{php_base}-devel
BuildRequires: %{php_base}-pear
BuildRequires: krb5-devel >= 1.8
BuildRequires: pkgconfig(com_err)

Requires(post): %{php_base}-pear
Requires(postun): %{php_base}-pear

Requires:     %{php_base}(zend-abi) = %{php_zend_api}
Requires:     %{php_base}(api) = %{php_core_api}

Provides:     php-%{pecl_name} = %{version}-%{release}
Provides:     php-%{pecl_name}%{?_isa} = %{version}-%{release}
Provides:     php-pecl(%{pecl_name}) = %{version}-%{release}
Provides:     php-pecl(%{pecl_name})%{?_isa} = %{version}-%{release}
Provides:     %{php_base}-%{pecl_name} = %{version}-%{release}
Provides:     %{php_base}-%{pecl_name}%{?_isa} = %{version}-%{release}
Provides:     %{php_base}-pecl(%{pecl_name}) = %{version}-%{release}
Provides:     %{php_base}-pecl(%{pecl_name})%{?_isa} = %{version}-%{release}

Provides:     %{real_name} = %{version}
Conflicts:    %{real_name} < %{version}


%description
Features:
 + An interface for maintaining credential caches (KRB5CCache),
   that can be used for authenticating against a kerberos5 realm
 + Bindings for nearly the complete GSSAPI (RFC2744)
 + The administrative interface (KADM5)
 + Support for HTTP Negotiate authentication via GSSAPI


%package devel
Summary:      Kerberos authentification extension developer files (header)
Group:        Development/Libraries

Requires:     %{php_base}(zend-abi) = %{php_zend_api}
Requires:     %{php_base}(api) = %{php_core_api}

Provides:     php-%{pecl_name}-devel = %{version}
Provides:     php-%{pecl_name}-devel%{?_isa} = %{version}
Provides:     php-pecl(%{pecl_name}-devel) = %{version}
Provides:     php-pecl(%{pecl_name}-devel)%{?_isa} = %{version}
Provides:     %{php_base}-%{pecl_name}-devel = %{version}
Provides:     %{php_base}-%{pecl_name}-devel%{?_isa} = %{version}
Provides:     %{php_base}-pecl(%{pecl_name}-devel) = %{version}
Provides:     %{php_base}-pecl(%{pecl_name}-devel)%{?_isa} = %{version}

Provides:     %{real_name}-devel = %{version}
Conflicts:    %{real_name}-devel < %{version}

%description devel
These are the files needed to compile programs using the Kerberos extension.

%prep
%setup -c -q
mv %{pecl_name}-%{version} NTS
cp -pr NTS ZTS
cat << 'EOF' | tee %{ini_name}
; Enable %{pecl_name} extension module
extension = %{pecl_name}.so
EOF


%build
export CFLAGS="%{optflags} $(pkg-config --cflags com_err)"
cd NTS
%{_bindir}/phpize
%configure  \
  --with-krb5 \
  --with-krb5kadm \
  --with-krb5config=%{_bindir}/krb5-config \
  --with-php-config=%{_bindir}/php-config
%{__make} %{?_smp_mflags}

cd ../ZTS
%{_bindir}/zts-phpize
%configure  \
  --with-krb5 \
  --with-krb5kadm \
  --with-krb5config=%{_bindir}/krb5-config \
  --with-php-config=%{_bindir}/zts-php-config
%{__make} %{?_smp_mflags}


%install
%{__make} -C NTS install INSTALL_ROOT=%{buildroot}

# Drop in the bit of configuration
%{__install} -Dm0644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
%{__install} -Dm0644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

make -C ZTS install INSTALL_ROOT=%{buildroot}
%{__install} -Dm0644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}

# Documentation
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do %{__install} -Dpm0644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ "$1" -eq "0" ]; then
   %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%check
: Minimal load test for NTS extension
%{__php} -n \
    -d extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    -i | grep "Kerberos 5 support => enabled"

: Minimal load test for ZTS extension
%{__ztsphp} -n \
    -d extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    -i | grep "Kerberos 5 support => enabled"


%files
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml
%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%files devel
%{php_incldir}/ext/%{pecl_name}
%{php_ztsincldir}/ext/%{pecl_name}


%changelog
* Sat Mar 22 2015 Joshua M. Keyes <joshua.michael.keyes@gmail.com> - 1.0.0-1
- Initial packaging.
