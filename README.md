<img alt="Impacket_light" src="https://github.com/user-attachments/assets/14aed700-0c6e-4865-ac53-686b91874f50" />

Impacket (Exegol fork)
======================

This is [ThePorgs](https://github.com/ThePorgs/Impacket)'s fork of [fortra/impacket](https://github.com/fortra/impacket). CLI banners print `Impacket (Exegol fork)`. Exegol ships this next to upstream Impacket (`*-og.py` aliases).

Upstream is slow to merge. This tree starts from `fortra/impacket` master and carries selected open PRs, one commit per PR, original authors kept. Conflicts were resolved here when needed.

Base: [`40b1eb7a`](https://github.com/fortra/impacket/commit/40b1eb7a) (PKINIT client, fortra/impacket#2260).

PRs added
---------

Links go to the original Fortra PRs.

### New example scripts

* [fortra/impacket#1224](https://github.com/fortra/impacket/pull/1224) `renameMachine.py`
* [fortra/impacket#2171](https://github.com/fortra/impacket/pull/2171) `gmsadump.py`
* [fortra/impacket#2079](https://github.com/fortra/impacket/pull/2079) `asreqUserCheck.py`
* [fortra/impacket#1256](https://github.com/fortra/impacket/pull/1256) `tgssub.py`
* [fortra/impacket#1731](https://github.com/fortra/impacket/pull/1731) `EditGroups.py`
* [fortra/impacket#2311](https://github.com/fortra/impacket/pull/2311) `negoex_parse_token.py`
* [fortra/impacket#2090](https://github.com/fortra/impacket/pull/2090) `getBootKey.py`
* [fortra/impacket#1618](https://github.com/fortra/impacket/pull/1618) `lookupname.py`
* [fortra/impacket#1280](https://github.com/fortra/impacket/pull/1280) `machineAccountQuota.py`
* [fortra/impacket#1941](https://github.com/fortra/impacket/pull/1941) `gmsaMembership.py`
* [fortra/impacket#2045](https://github.com/fortra/impacket/pull/2045) `ldap_shell.py`
* [fortra/impacket#2240](https://github.com/fortra/impacket/pull/2240) `rpcclient.py`
* [fortra/impacket#1994](https://github.com/fortra/impacket/pull/1994) `adidns.py` + `impacket/dnsp.py`
* [fortra/impacket#2033](https://github.com/fortra/impacket/pull/2033) `winrmexec.py` + `impacket/winrm.py`

### ntlmrelayx / LDAP attacks

* [fortra/impacket#2345](https://github.com/fortra/impacket/pull/2345) SMB/LDAP signing bypass (`--reauth-bypass`)
* [fortra/impacket#2073](https://github.com/fortra/impacket/pull/2073) SCCM Client Push relay (`--sccm-clientpush`)
* [fortra/impacket#1288](https://github.com/fortra/impacket/pull/1288) CVE-2021-34470 computer-create bypass
* [fortra/impacket#1154](https://github.com/fortra/impacket/pull/1154) ACL attack: allow computer accounts
* [fortra/impacket#2328](https://github.com/fortra/impacket/pull/2328) Shadow credentials improvements
* [fortra/impacket#2287](https://github.com/fortra/impacket/pull/2287) HTTP SOCKS relay body corruption fix

### Kerberos / tickets

* [fortra/impacket#2324](https://github.com/fortra/impacket/pull/2324) `getST.py` S4U2Proxy + U2U (`-nospn`)
* [fortra/impacket#2192](https://github.com/fortra/impacket/pull/2192) PA-FOR-USER checksum on WS2025
* [fortra/impacket#2326](https://github.com/fortra/impacket/pull/2326) GetUserSPNs honors `-dc-ip` in no-preauth
* [fortra/impacket#2331](https://github.com/fortra/impacket/pull/2331) GetUserSPNs AES salt from KDC
* [fortra/impacket#2317](https://github.com/fortra/impacket/pull/2317) MIT Kerberos AS replies + TGS checksums
* [fortra/impacket#2351](https://github.com/fortra/impacket/pull/2351) Inter-realm referral TGT from ccache
* [fortra/impacket#2318](https://github.com/fortra/impacket/pull/2318) Ccache SPN matching
* [fortra/impacket#2303](https://github.com/fortra/impacket/pull/2303) Stop hanging on a silent KDC
* [fortra/impacket#2316](https://github.com/fortra/impacket/pull/2316) Pad empty AES GSS wrap
* [fortra/impacket#2335](https://github.com/fortra/impacket/pull/2335) Kerberos AES PBKDF2 C implementation
* [fortra/impacket#2086](https://github.com/fortra/impacket/pull/2086) Ticket files chmod 600
* [fortra/impacket#2348](https://github.com/fortra/impacket/pull/2348) Missing Kerberos etype names
* [fortra/impacket#2244](https://github.com/fortra/impacket/pull/2244) MSSQL named-pipe Kerberos ticket selection

### SMB / DCERPC / WMI / other library

* [fortra/impacket#2220](https://github.com/fortra/impacket/pull/2220) SMB 3.0.2 dialect
* [fortra/impacket#2339](https://github.com/fortra/impacket/pull/2339) SMB2/3 SPNEGO mechListMIC
* [fortra/impacket#2302](https://github.com/fortra/impacket/pull/2302) Stop leaking client OS/hostname
* [fortra/impacket#2297](https://github.com/fortra/impacket/pull/2297) SMB2 high-latency read timeout
* [fortra/impacket#2280](https://github.com/fortra/impacket/pull/2280) SMB share type reporting
* [fortra/impacket#2342](https://github.com/fortra/impacket/pull/2342) smbserver: open existing dirs read-only
* [fortra/impacket#2330](https://github.com/fortra/impacket/pull/2330) Move `WIN_VERSIONS` to smb3structs
* [fortra/impacket#2341](https://github.com/fortra/impacket/pull/2341) DCERPC transports raise `DCERPCException`
* [fortra/impacket#2296](https://github.com/fortra/impacket/pull/2296) WMI Next() last batch + ExecMethod errors
* [fortra/impacket#2272](https://github.com/fortra/impacket/pull/2272) WMI kwargs-style method calls
* [fortra/impacket#2323](https://github.com/fortra/impacket/pull/2323) Keep SACL when DACL is absent
* [fortra/impacket#2270](https://github.com/fortra/impacket/pull/2270) ESE 32KB pages (WS2025 NTDS)
* [fortra/impacket#2232](https://github.com/fortra/impacket/pull/2232) MS-CAPR
* [fortra/impacket#2347](https://github.com/fortra/impacket/pull/2347) DPAPI stdlib HMAC
* [fortra/impacket#2308](https://github.com/fortra/impacket/pull/2308) winregistry read-only open flags
* [fortra/impacket#2349](https://github.com/fortra/impacket/pull/2349) lookupsid `-lookup-domain` / `-lookup-name`
* [fortra/impacket#1698](https://github.com/fortra/impacket/pull/1698) secretsdump `-inline` / `-restore` (ported onto current secretsdump)
* [fortra/impacket#2336](https://github.com/fortra/impacket/pull/2336) Wait for RemoteRegistry instead of sleep(1)

Not taken this run
------------------

* [fortra/impacket#2290](https://github.com/fortra/impacket/pull/2290) already in upstream master
* [fortra/impacket#2350](https://github.com/fortra/impacket/pull/2350) redundant with #2296
* [fortra/impacket#2157](https://github.com/fortra/impacket/pull/2157) cross-forest RBCD: would rewrite `getKerberosTGS` / S4U and undo #2324, #2192, #2317, #2303

Upstream Impacket
=================

Copyright Fortra, LLC and its affiliated companies. All rights reserved.

Impacket was originally created by [SecureAuth](https://www.secureauth.com/labs/open-source-tools/impacket), and now maintained by Fortra's Core Security.

Impacket is a collection of Python classes for working with network
protocols. Impacket is focused on providing low-level
programmatic access to the packets and for some protocols (e.g.
SMB1-3 and MSRPC) the protocol implementation itself.
Packets can be constructed from scratch, as well as parsed from
raw data, and the object-oriented API makes it simple to work with
deep hierarchies of protocols. The library provides a set of tools
as examples of what can be done within the context of this library.

What protocols are featured?
----------------------------

 * Ethernet, Linux "Cooked" capture.
 * IP, TCP, UDP, ICMP, IGMP, ARP.
 * IPv4 and IPv6 Support.
 * NMB and SMB1, SMB2 and SMB3 (high-level implementations).
 * MSRPC version 5, over different transports: TCP, SMB/TCP, SMB/NetBIOS and HTTP.
 * Plain, NTLM and Kerberos authentications, using password/hashes/tickets/keys.
 * Portions/full implementation of the following MSRPC interfaces: EPM, DTYPES, LSAD, LSAT, NRPC, RRP, SAMR, SRVS, WKST, SCMR, BKRP, DHCPM, EVEN6, MGMT, SASEC, TSCH, DCOM, WMI, OXABREF, NSPI, OXNSPI.
 * Portions of TDS (MSSQL) and LDAP protocol implementations.

This fork
=========

Maintained for Exegol. Do not open feature PRs against Fortra here; open them upstream and they can be pulled on the next fork refresh.

Table of Contents
=================

* [Getting Impacket](#getting-impacket)
* [Setup](#setup)
* [Testing](#testing)
* [Licensing](#licensing)
* [Disclaimer](#disclaimer)
* [Contact Us](#contact-us)

Getting Impacket
================

### This fork

```
python3 -m pipx install git+https://github.com/ThePorgs/Impacket.git
```

Or clone and `python3 -m pipx install .`

### Upstream latest version

* Impacket v0.13.1

  [![Python versions](https://img.shields.io/pypi/pyversions/impacket.svg)](https://pypi.python.org/pypi/impacket/)

[Current and past releases](https://github.com/fortra/impacket/releases)

### Upstream development version

* Impacket v0.14.0-dev (**[master branch](https://github.com/fortra/impacket/tree/master)**)

Setup
=====

### Quick start

> :information_source: We recommend using `pipx` over `pip` for system-wide installations.

    python3 -m pipx install git+https://github.com/ThePorgs/Impacket.git

### Docker Support

Build Impacket's image:

      $ docker build -t "impacket:latest" .

Using Impacket's image:

      $ docker run -it --rm "impacket:latest"

Testing
=======

The library leverages the [pytest](https://docs.pytest.org/) framework for organizing
and marking test cases, [tox](https://tox.readthedocs.io/) to automate the process of
running them across supported Python versions, and [coverage](https://coverage.readthedocs.io/)
to obtain coverage statistics.

A [comprehensive testing guide](TESTING.md) is available.


Licensing
=========

This software is provided under a slightly modified version of
the Apache Software License. See the accompanying [LICENSE](LICENSE) file for
more information.

SMBv1 and NetBIOS support based on Pysmb by Michael Teo.

Disclaimer
==========

The spirit of this Open Source initiative is to help security researchers,
and the community, speed up research and educational activities related to
the implementation of networking protocols and stacks.

The information in this repository is for research and educational purposes
and not meant to be used in production environments and/or as part
of commercial products.

If you desire to use this code or some part of it for your own uses, we
recommend applying proper security development life cycle and secure coding
practices, as well as generate and track the respective indicators of
compromise according to your needs.


## Contact Us

For this fork: [ThePorgs/Impacket](https://github.com/ThePorgs/Impacket/issues).

For general questions, bug reports, or feature requests against upstream Impacket, use [fortra/impacket](https://github.com/fortra/impacket/issues).

If you believe you have discovered a security vulnerability in Impacket, follow the instructions in the [Security Policy](SECURITY.md).
