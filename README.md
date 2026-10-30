<img alt="Impacket_light" src="https://github.com/user-attachments/assets/14aed700-0c6e-4865-ac53-686b91874f50" />

Impacket (Exegol fork)
======================

This is [ThePorgs](https://github.com/ThePorgs/Impacket)'s fork of [fortra/impacket](https://github.com/fortra/impacket). CLI banners print `Impacket (Exegol fork)`. Exegol ships this next to upstream Impacket (`*-og.py` aliases).

Upstream is slow to merge. This tree starts from `fortra/impacket` master and carries selected open PRs, one commit per PR, original authors kept. Conflicts were resolved here when needed. This fork is to be considered bleeding-edge, and AI was heavily used to select, merge and resolve conflicts. This means that this fork is to be considered less stable than origin.

This forks is maintained for Exegol. Do not open feature PRs against Fortra here; open them upstream and they can be pulled on the next fork refresh.

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

Upstream Impacket
=================

Copyright Fortra, LLC and its affiliated companies. All rights reserved.

Impacket was originally created by [SecureAuth](https://www.secureauth.com/labs/open-source-tools/impacket), and now maintained by Fortra's Core Security.