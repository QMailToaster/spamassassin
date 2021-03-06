%define    real_name Mail-SpamAssassin
Name:      spamassassin
Summary:   Spam filter for email which can be invoked from mail agents.
Version:   3.4.0
Release:   2%{?dist}
License:   Apache License
Group:     Applications/Internet
Vendor:    QmailToaster
Packager:  Eric Shubert <qmt-build@datamatters.us>
URL:       http://spamassassin.apache.org/
Source0:   http://supergsego.com/apache/%{name}/source/Mail-SpamAssassin-%{version}.tar.gz
Source1:   spamassassin.v310.pre
Source2:   spamassassin.local.cf
Source3:   sa-update
Source4:   spamassassin.sysconfig
Patch0:    v340-util.patch
BuildRequires:  perl >= 5.8.8
%if %{?fedora}0 > 140 || %{?rhel}0 > 50
BuildRequires:  perl-ExtUtils-MakeMaker
%endif
BuildRequires:  openssl-devel 
BuildRequires:  perl(Archive::Tar)
BuildRequires:  perl(Digest::SHA)
BuildRequires:  perl(HTML::Parser)
BuildRequires:  perl(IO::Zlib)
BuildRequires:  perl(Net::DNS)
BuildRequires:  perl(NetAddr::IP)
BuildRequires:  perl(Time::HiRes)
Requires:  curl
Requires:  perl(Archive::Tar)
Requires:  perl(Compress::Zlib)
Requires:  perl(Crypt::OpenSSL::Bignum)
Requires:  perl(DB_File)
Requires:  perl(DBI)
Requires:  perl(Digest::SHA1)
Requires:  perl(Encode::Detect)
Requires:  perl(Geo::IP)
Requires:  perl(Getopt::Long)
Requires:  perl(HTML::Parser)
# IO::Socket::IP is optional, but provides cleaner IP support
# regardless of family (IPV4/IPV6). New with v3.4.0
#Requires:  perl(IO::Socket::IP)
Requires:  perl(IO::Socket::SSL)
Requires:  perl(IO::Zlib)
Requires:  perl(Mail::DKIM)
Requires:  perl(Mail::DomainKeys)
Requires:  perl(Mail::SPF::Query)
Requires:  perl(MIME::Base64)
Requires:  perl(Net::DNS)
Requires:  perl(Net::SMTP)
Requires:  perl(NetAddr::IP)
# shubes 12/23/13 - repoforge doesn't see the (::) format for this one
# Steve H has fixed, need to wait for rebuild
Requires:  perl-Razor-Agent
Requires:  perl(Time::HiRes)
Requires:  perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires:  gnupg
Requires:  procmail
Requires:  qmail
Requires:  vpopmail
Obsoletes: perl-Mail-SpamAssassin
Obsoletes: spamassassin-toaster
Obsoletes: perl-spamassassin
BuildRoot: %{_topdir}/BUILDROOT/%{name}-%{version}-%{release}.%{_arch}

%define debug_package %{nil}
%define _use_internal_dependency_generator 0
%define krb5backcompat %([ -a /usr/kerberos/include/krb5.h ] && echo 1 || echo 0)
%{!?perl_vendorlib: %define perl_vendorlib %(eval "`%{__perl} -V:installvendorlib`"; echo $installvendorlib)}

#-------------------------------------------------------------------------------
%description
#-------------------------------------------------------------------------------
SpamAssassin provides you with a way to reduce if not completely eliminate
Unsolicited Commercial Email (SPAM) from your incoming email.  It can
be invoked by a MDA such as sendmail or postfix, or can be called from
a procmail script, .forward file, etc.  It uses a genetic-algorithm
evolved scoring system to identify messages which look spammy, then
adds headers to the message so they can be filtered by the user's mail
reading software.  This distribution includes the spamd/spamc components
which create a server that considerably speeds processing of mail.

#-------------------------------------------------------------------------------
%prep
#-------------------------------------------------------------------------------

%setup -q -n Mail-SpamAssassin-%{version}
%patch0 -p0

#-------------------------------------------------------------------------------
%build
#-------------------------------------------------------------------------------
%{__perl} Makefile.PL \
      DESTDIR=%{buildroot}/ \
      SYSCONFDIR=%{_sysconfdir} \
      INSTALLDIRS=vendor \
      ENABLE_SSL=yes \
      LOCALRULESDIR=%{_sysconfdir}/%{name} \
      < /dev/null

%{__make} %{?krb5backcompat:SSLCFLAGS=-DSPAMC_SSL\ -I/usr/kerberos/include} \
      OPTIMIZE="%{optflags}"

#-------------------------------------------------------------------------------
%install
#-------------------------------------------------------------------------------
%define saconfdir  %{buildroot}%{_sysconfdir}/%{name}
%define _initpath  %{_sysconfdir}/rc.d/init.d

rm -rf %{buildroot}

%makeinstall PREFIX=%{buildroot}%{_prefix} \
     INSTALLMAN1DIR=%{buildroot}%{_mandir}/man1 \
     INSTALLMAN3DIR=%{buildroot}%{_mandir}/man3 \
     LOCAL_RULES_DIR=%{saconfdir}
chmod 755 %{buildroot}%{_bindir}/* # allow stripping

[ -x /usr/lib/rpm/brp-compress ] && /usr/lib/rpm/brp-compress

find %{buildroot} \( -name perllocal.pod -o -name .packlist \) -exec rm -v {} \;
find %{buildroot} -type d -depth -exec rmdir {} 2>/dev/null ';'

find %{buildroot}/usr -type f -print |
        sed "s@^%{buildroot}@@g" |
        grep -v perllocal.pod |
        grep -v "\.packlist" > %{name}-%{version}-filelist
if [ "$(cat %{name}-%{version}-filelist)X" = "X" ] ; then
    echo "ERROR: EMPTY FILE LIST"
    exit -1
fi
find %{buildroot}%{perl_vendorlib}/* -type d -print |
        sed "s@^%{buildroot}@%dir @g" >> %{name}-%{version}-filelist

rm -f %{saconfdir}/init.pre
%{__install} -Dp %{_builddir}/%{real_name}-%{version}/rules/v312.pre \
                             %{saconfdir}/v312.pre
%{__install}     %{_builddir}/%{real_name}-%{version}/rules/v320.pre \
                             %{saconfdir}/v320.pre

%{__install} %{SOURCE1}      %{saconfdir}/v310.pre
%{__install} %{SOURCE2}      %{saconfdir}/local.cf

%{__install} -Dp %{SOURCE3}  %{buildroot}%{_sysconfdir}/cron.daily/sa-update
%{__install} -Dp %{SOURCE4}  %{buildroot}%{_sysconfdir}/sysconfig/%{name}
 
%{__install} -d              %{buildroot}%{_initpath}
%{__install} %{_builddir}/%{real_name}-%{version}/spamd/redhat-rc-script.sh \
                             %{buildroot}%{_initpath}/spamd

#-------------------------------------------------------------------------------
%clean
#-------------------------------------------------------------------------------
rm -rf %{_builddir}/%{real_name}-%{version}
rm -rf %{buildroot}

#-------------------------------------------------------------------------------
%pre
#-------------------------------------------------------------------------------

# remove qtp-sa-update cron job if it exists
if [ -f /etc/cron.daily/qtp-sa-update ]; then
  rm -f /etc/cron.daily/qtp-sa-update
fi

#-------------------------------------------------------------------------------
%preun
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
%post
#-------------------------------------------------------------------------------

# stop spamd and move supervise scripts if present
oldsupdir=/var/qmail/supervise/spamd
if [ ! -z "$(which svc 2>/dev/null)" ] \
      && [ -d "$oldsupdir" ]; then
  svc -d $oldsupdir
  mv $oldsupdir /root/spamd.supervise
fi

# rename old configuration directory to minimize confusion
# and bring customized local.cf forward to new config directory
oldspamconf=/etc/mail/spamassassin
newspamconf=/etc/spamassassin
if [ -d "$oldspamconf" ]; then
  if [ -f $oldspamconf/local.cf ]; then
    mv $newspamconf/local.cf     $newspamconf/local.cf.rpmnew
    cp -p $oldspamconf/local.cf  $newspamconf/local.cf
  elif [ -f $oldspamconf/local.cf.rpmsave ]; then
#   this probably will never really happen, but I'm not absolutely certain
    mv $newspamconf/local.cf            $newspamconf/local.cf.rpmnew
    cp -p $oldspamconf/local.cf.rpmsave $newspamconf/local.cf
  fi
  mv $oldspamconf $oldspamconf.old
fi

# send SIGHUP to spamd when log rotates
logrfile=/etc/logrotate.d/syslog
if [ -f "$logrfile" ]; then
  grep -q spamd\.pid $logrfile || \
        sed -i '/\/bin\/kill/ a\
	/bin/kill -HUP `cat /var/run/spamd.pid 2> /dev/null` 2> /dev/null || true' \
        $logrfile
fi

/sbin/chkconfig --add spamd
/sbin/chkconfig spamd on

# update (or get) the sa rules, and restart spamd if it's running
/etc/cron.daily/sa-update -r

# if spamd is not running, start it
if [ ! -e /var/lock/subsys/spamd ]; then
  /sbin/service spamd start >/dev/null 2>&1
fi

#-------------------------------------------------------------------------------
%postun
#-------------------------------------------------------------------------------

if [ $1 = "0" ]; then
  rm -fR /var/qmail/supervise/spamd/
fi
#-------------------------------------------------------------------------------
# triggerin is executed after spamassassin is installed, if simscan is installed
# *and* after simscan is installed while spamassassin is installed
#-------------------------------------------------------------------------------
%triggerin -- simscan-toaster
#-------------------------------------------------------------------------------
if [ -x /var/qmail/bin/update-simscan ]; then
  /var/qmail/bin/update-simscan
fi

#-------------------------------------------------------------------------------
%files -f %{name}-%{version}-filelist
#-------------------------------------------------------------------------------
%defattr(-,root,root)

# Docs
%doc LICENSE CREDITS Changes README TRADEMARK UPGRADE
%doc USAGE sample-nonspam.txt sample-spam.txt

# Dirs
%attr(0755,root,root)    %dir %{_sysconfdir}/%{name}

# Files
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/%{name}/local.cf
%config            %attr(0644,root,root) %{_sysconfdir}/%{name}/v310.pre
%config            %attr(0644,root,root) %{_sysconfdir}/%{name}/v312.pre
%config            %attr(0644,root,root) %{_sysconfdir}/%{name}/v320.pre
%config            %attr(0644,root,root) %{_sysconfdir}/%{name}/v330.pre
%config            %attr(0644,root,root) %{_sysconfdir}/%{name}/v340.pre
%config            %attr(0644,root,root) %{_sysconfdir}/sysconfig/%{name}

# Executables
%attr(0755,root,root)     %{_sysconfdir}/cron.daily/sa-update
%attr(0755,root,root)     %{_initpath}/spamd

#-------------------------------------------------------------------------------
%changelog
#-------------------------------------------------------------------------------
* Thu Sep 18 2014 Eric Shubert <eric@datamatters.us> 3.4.0-2.qt
- Fixed sa-update to restart conditionally, and run sa-update from %post
- Fixed local.cf retention
* Mon Sep 15 2014 Eric Shubert <eric@datamatters.us> 3.4.0-1.qt
- fixed sa-update to use 'service' instead of 'svc'
- patched Util.pm for spamd -x bug #7015
- retain local.cf from its old location
* Mon Sep  8 2014 Eric Shubert <eric@datamatters.us> 3.4.0-0.qt
- upgraded to upstreadm 3.4.0 version
- moved configuration files to /etc/spamassassin
- modified v3xx.pre file to replace (removed noreplace)
* Tue Jul  8 2014 Eric Shubert <eric@datamatters.us> 3.3.2-2.qt
- Modified to use init script instead of supervise
* Mon Apr 07 2014 Eric Shubert <eric@datamatters.us> 3.3.2-1.qt
- Modified to use syslog
* Sat Nov 16 2013 Eric Shubert <eric@datamatters.us> 3.3.2-0.qt
- Migrated to repoforge
- Removed -toaster designation
- Added CentOS 6 support
- Remove unsupported cruft
* Sun Jul 29 2012 Eric Shubert <eric@datamatters.us> 3.3.2-1.4.3
- Fixed bug with removing qtp-sa-update
* Sat Jul 28 2012 Eric Shubert <eric@datamatters.us> 3.3.2-1.4.2
- Uncommented sa-update cron job (thanks to Aleksander P)
- Removed stdout output from sa-update.cron (log output only)
- Removed /etc/cron.daily/qtp-sa-update (thanks to Aleksander P)
* Thu Jul 26 2012 Eric Shubert <eric@datamatters.us> 3.3.2-1.4.1
- Added cron job to run sa-update (courtesy of repoforge)
- Added sa-update.log, logrotate conf (courtesy of repoforge)
- Added sa-update to %post
* Tue Jul 24 2012 Eric Shubert <eric@datamatters.us> 3.3.2-1.4.0
- Bumped QMT version to 1.4.0
- Added trigger to update simscan
- Removed DomainKeys plugin from v310.pre
* Fri Oct 07 2011 Jake Vickers <jake@qmailtoaster.com> 3.3.2-1.3.18
- Updated spamassassin to version 3.3.2
* Fri Jun 12 2009 Jake Vickers <jake@qmailtoaster.com> 3.2.5-1.3.17
- Added Fedora 11 support
- Added Fedora 11 x86_64 support
* Wed Jun 10 2009 Jake Vickers <jake@qmailtoaster.com> 3.2.5-1.3.17
- Added Mandriva 2009 support
* Thu Apr 23 2009 Jake Vickers <jake@qmailtoaster.com> 3.2.5-1.3.16
- Added Fedora 9 x86_64 and Fedora 10 x86_64 support
- Fixed a bug in installation of /etc/mail/spamassassin files that may have
- caused it to no build/install on certain systems
* Mon Feb 16 2009 Jake Vickers <jake@qmailtoaster.com> 3.2.5-1.3.15
- Added Suse 11.1 support
* Mon Feb 09 2009 Jake Vickers <jake@qmailtoaster.com> 3.2.5-1.3.15
- Added Fedora 9 and 10 support
* Fri Jul 11 2008 Erik A. Espinoza <espinoza@kabewm.com> 3.2.5-1.3.14
- Upgraded to SpamAssassin 3.2.5
* Sun Feb 04 2008 Erik A. Espinoza <espinoza@kabewm.com> 3.2.4-1.3.13
- Upgraded to SpamAssassin 3.2.4
* Thu Aug 09 2007 Erik A. Espinoza <espinoza@kabewm.com> 3.2.3-1.3.12
- Upgraded to SpamAssassin 3.2.3
* Tue Aug 07 2007 Erik A. Espinoza <espinoza@kabewm.com> 3.2.2-1.3.11
- Upgraded to SpamAssassin 3.2.2
* Mon Jun 18 2007 Erik A. Espinoza <espinoza@kabewm.com> 3.2.1-1.3.10
- Upgraded to SpamAssassin 3.2.1
* Mon May 21 2007 Erik A. Espinoza <espinoza@kabewm.com> 3.2.0-1.3.9
- Upgraded to SpamAssassin 3.2.0
* Sat Apr 14 2007 Nick Hemmesch <nick@ndhsoft.com> 3.1.8-1.3.8
- Added CentOS 5 i386 support
- Added CentOS 5 x86_64 support
* Sat Feb 24 2007 Erik A. Espinoza <espinoza@kabewm.com> 3.1.8-1.3.7
- Upgraded to SpamAssassin 3.1.8
- Made local.cf, v310.pre and v312.pre into config for easier upgrades
* Wed Nov 01 2006 Erik A. Espinoza <espinoza@forcenetworks.com> 3.1.7-1.3.6
- Added Fedora Core 6 support
- Changed "required_hits" to "required_score" as the old option has been deprecated
* Sat Oct 14 2006 Erik A. Espinoza <espinoza@forcenetworks.com> 3.1.7-1.3.5
- Upgraded to SpamAssassin 3.1.7
* Sat Oct 07 2006 Erik A. Espinoza <espinoza@forcenetworks.com> 3.1.6-1.3.4
- Upgraded to SpamAssassin 3.1.6
- Removed "-L", local checks only setting
* Sun Sep 10 2006 Erik A. Espinoza <espinoza@forcenetworks.com> 3.1.5-1.3.3
- Upgraded to SpamAssassin 3.1.5
* Sat Aug 05 2006 Erik A. Espinoza <espinoza@forcenetworks.com> 3.1.4-1.3.2
- Upgraded to SpamAssassin 3.1.4
* Tue Jun 06 2006 John Li <jli@jlisbz.com> 3.1.3-1.3.1
- Upgraded to SpamAssassin 3.1.3
- Ticked branch to 1.3
* Sun May 28 2006 Erik A. Espinoza <espinoza@forcenetworks.com> 3.1.2-1.2.16
- Upgraded to spamassassin 3.1.2
* Tue May 16 2006 Nick Hemmesch <nick@ndhsoft.com> 3.1.1-1.2.15
- Added SuSE 10.1 support
* Sat May 13 2006 Nick Hemmesch <nick@ndhsoft.com> 3.1.1-1.2.14
- Added Fedora Core 5 support
* Sun Apr 30 2006 Erik A. Espinoza <espinoza@forcenetworks.com> 3.1.1-1.2.13
- Fixed spec file to clean build root properly
- Reoved spam-sync cron job
* Tue Apr 10 2006 Erik A. Espinoza <espinoza@forcenetworks.com> 3.1.1-1.2.12
- Updated to spamassassin 3.1.1
* Tue Dec 06 2005 Nick Hemmesch <nick@ndhsoft.com> 3.1.0-1.2.11
- Fix bayes_auto_learn and sa-learn functions
- Update local.cf and v310.pre
- Add sa-learn --sync call to cron.hourly
* Sun Nov 20 2005 Nick Hemmesch <nick@ndhsoft.com> 3.1.0-1.2.10
- Add SuSE 10.0 and Mandriva 2006.0 support
* Sat Oct 15 2005 Nick Hemmesch <nick@ndhsoft.com> 3.0.4-1.2.9
- Add Fedora Core 4 x86_64 support
* Sat Oct 01 2005 Nick Hemmesch <nick@ndhsoft.com> 3.0.4-1.2.8
- Add CentOS 4 x86_64 support
* Mon Sep 26 2005 Nick Hemmesch <nick@ndhsoft.com> 3.1.0-1.2.7
- Update local.cf and dirs for spamassassin 3.1.0
* Tue Sep 20 2005 Erik A. Espinoza <espinoza@forcenetworks.com> 3.1.0-1.2.6
- Upgraded to spamassassin 3.1.0
* Thu Jul 28 2005 Nick Hemmesch <nick@ndhsoft.com> 3.0.4-1.2.5
- Fix auto-whitelist - change from a dir to a file
* Mon Jul 04 2005 Nick Hemmesch <nick@ndhsoft.com> 3.0.4-1.2.4
- Fix perl-forward-compat problem with rht90 
* Fri Jul 01 2005 Nick Hemmesch <nick@ndhsoft.com> 3.0.4-1.2.4
- Add support for Fedora Core 4
* Sun Jun 19 2005 Nick Hemmesch <nick@ndhsoft.com> 3.0.4-1.2.3
- Update to spamassassin-3.0.4
* Fri Jun 03 2005 Torbjorn Turpeinen <tobbe@nyvalls.se> 3.0.1-1.2.2
- Gnu/Linux Mandrake 10.0,10.1,10.2 support
* Mon May 30 2005 Nick Hemmesch <nick@ndhsoft.com> - 3.0.1-1.2.1
- Intitial build to work with qmail-toaster and simscan-toaster
