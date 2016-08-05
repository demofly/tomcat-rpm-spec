%define __jar_repack %{nil}
%define tomcat_group tomcat
%define tomcat_user tomcat
%define tomcat_home /usr/share/uostomcat
%define tomcat_user_home /srv/tomcat
%define tomcat_cache_home /var/cache/uostomcat
%define tomcat_conf_home %{_sysconfdir}/uostomcat
%define tomcat_log_home /var/log/uostomcat
%define systemd_dir /usr/lib/systemd/system/

Summary:    Apache Servlet/JSP Engine, RI for Servlet 3.1/JSP 2.3 API
Name:       uostomcat
Version:    8.5.4
BuildArch:  noarch
Release:    4
License:    Apache Software License
Group:      Networking/Daemons
URL:        http://tomcat.apache.org/
Source0:    apache-tomcat-%{version}.tar.gz
Source1:    %{name}.service
Source2:    %{name}.sysconfig
Source3:    %{name}.logrotate
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Tomcat is the servlet container that is used in the official Reference
Implementation for the Java Servlet and JavaServer Pages technologies.
The Java Servlet and JavaServer Pages specifications are developed by
Oracle under the Java Community Process.

Tomcat is developed in an open and participatory environment and
released under the Apache Software License. Tomcat is intended to be
a collaboration of the best-of-breed developers from around the world.
We invite you to participate in this open development project. To
learn more about getting involved, click here.

This package contains the base tomcat installation that depends on Oracle's JDK 
and not on JPP packages.

%prep
%setup -q -n apache-tomcat-%{version}

%build

%install
install -d -m 755 %{buildroot}/%{tomcat_home}/
cp -R * %{buildroot}/%{tomcat_home}/

# Remove all webapps. Put webapps in a custom location and link back.
rm -rf %{buildroot}/%{tomcat_home}/webapps
install -d -m 775 %{buildroot}%{tomcat_user_home}/webapps
cd %{buildroot}/%{tomcat_home}/
ln -s %{tomcat_user_home}/webapps webapps
chmod 775 %{buildroot}/%{tomcat_user_home}
cd -

# Remove windows bat files
rm -f %{buildroot}/%{tomcat_home}/bin/*.bat

# Remove the 'safeToDelete.tmp'
rm -f %{buildroot}/%{tomcat_home}/temp/safeToDelete.tmp

# Remove useless doc files
rm -f %{buildroot}/%{tomcat_home}/LICENSE
rm -f %{buildroot}/%{tomcat_home}/NOTICE
rm -f %{buildroot}/%{tomcat_home}/RELEASE-NOTES
rm -f %{buildroot}/%{tomcat_home}/RUNNING.txt

# Put logging in a custom location and link back.
rm -rf %{buildroot}/%{tomcat_home}/logs
install -d -m 755 %{buildroot}%{tomcat_log_home}/
cd %{buildroot}/%{tomcat_home}/
ln -s %{tomcat_log_home}/ logs
cd -

# Put conf in a custom location and link back.
install -d -m 755 %{buildroot}/%{_sysconfdir}
mv %{buildroot}/%{tomcat_home}/conf %{buildroot}/%{tomcat_conf_home}
cd %{buildroot}/%{tomcat_home}/
ln -s %{tomcat_conf_home} conf
cd -

# Put temp and work in a custom location and link back.
install -d -m 775 %{buildroot}%{tomcat_cache_home}
mv %{buildroot}/%{tomcat_home}/temp %{buildroot}/%{tomcat_cache_home}/
mv %{buildroot}/%{tomcat_home}/work %{buildroot}/%{tomcat_cache_home}/
cd %{buildroot}/%{tomcat_home}/
ln -s %{tomcat_cache_home}/temp
ln -s %{tomcat_cache_home}/work
chmod 775 %{buildroot}/%{tomcat_cache_home}/temp
chmod 775 %{buildroot}/%{tomcat_cache_home}/work
cd -

# systemd service
install -d -m 755 %{buildroot}/%{systemd_dir}
install    -m 644 %_sourcedir/%{name}.service %{buildroot}/%{systemd_dir}/%{name}.service

# sysconfig script
install -d -m 755 %{buildroot}/%{_sysconfdir}/sysconfig/
install    -m 644 %_sourcedir/%{name}.sysconfig %{buildroot}/%{_sysconfdir}/sysconfig/%{name}

# logrotate script
install -d -m 755 %{buildroot}/%{_sysconfdir}/logrotate.d
install    -m 644 %_sourcedir/%{name}.logrotate %{buildroot}/%{_sysconfdir}/logrotate.d/%{name}

%clean
rm -rf %{buildroot}

%pre
getent group %{tomcat_group} >/dev/null || groupadd -g 91 -r %{tomcat_group}
getent passwd %{tomcat_user} >/dev/null || /usr/sbin/useradd -u 91 --comment "Apache Tomcat" --shell /sbin/nologin -M -r -g %{tomcat_group} --home %{tomcat_home} %{tomcat_user}

%files
%defattr(-,%{tomcat_user},%{tomcat_group},0770)
%{tomcat_log_home}/
%defattr(-,root,root)
%{tomcat_user_home}
%{tomcat_home}
%{systemd_dir}/%{name}.service
%{_sysconfdir}/logrotate.d/%{name}
%defattr(-,root,%{tomcat_group})
%{tomcat_cache_home}
%{tomcat_cache_home}/temp
%{tomcat_cache_home}/work
%{tomcat_user_home}/webapps
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{tomcat_conf_home}/*

%post
/bin/systemctl daemon-reload
