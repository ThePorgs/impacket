import socket
import struct
import threading
import time
from unittest import TestCase, mock

from pyasn1.codec.der import decoder, encoder
from pyasn1.type.univ import noValue

from impacket.krb5 import constants
from impacket.krb5.asn1 import AS_REP, TGS_REQ, seq_set
from impacket.krb5.kerberosv5 import DEFAULT_TGS_ENCTYPES, RC4_PREFERRED_TGS_ENCTYPES, KerberosError, \
    getKerberosTGS, getKerberosTGSRequestEnctypes, sendReceive
from impacket.krb5.types import Principal


class _RC4Cipher:
    enctype = constants.EncryptionTypes.rc4_hmac.value

    @staticmethod
    def encrypt(key, keyUsage, data, iv):
        return b'encrypted-authenticator'


def _build_rc4_tgt(tgtService='krbtgt/EXAMPLE.COM', ticketRealm='EXAMPLE.COM'):
    asRep = AS_REP()
    asRep['pvno'] = 5
    asRep['msg-type'] = constants.ApplicationTagNumbers.AS_REP.value
    asRep['crealm'] = ticketRealm
    seq_set(
        asRep,
        'cname',
        Principal('user', type=constants.PrincipalNameType.NT_PRINCIPAL.value).components_to_asn1,
    )

    asRep['ticket'] = noValue
    asRep['ticket']['tkt-vno'] = 5
    asRep['ticket']['realm'] = ticketRealm
    seq_set(
        asRep['ticket'],
        'sname',
        Principal(
            tgtService,
            type=constants.PrincipalNameType.NT_SRV_INST.value,
        ).components_to_asn1,
    )
    asRep['ticket']['enc-part'] = noValue
    asRep['ticket']['enc-part']['etype'] = constants.EncryptionTypes.rc4_hmac.value
    asRep['ticket']['enc-part']['cipher'] = b'ticket'

    asRep['enc-part'] = noValue
    asRep['enc-part']['etype'] = constants.EncryptionTypes.rc4_hmac.value
    asRep['enc-part']['cipher'] = b'reply'
    return encoder.encode(asRep)


class KerberosTGSEnctypeTests(TestCase):
    def _assert_request_enctypes(self, requestedEtypes, expectedEtypes):
        requests = []

        def capture_request(data, domain, kdcHost, timeout=None):
            tgsReq = decoder.decode(data, asn1Spec=TGS_REQ())[0]
            requests.append(tuple(int(etype) for etype in tgsReq['req-body']['etype']))
            raise KerberosError(constants.ErrorCodes.KDC_ERR_ETYPE_NOSUPP.value)

        with mock.patch('impacket.krb5.kerberosv5.sendReceive', side_effect=capture_request) as sendReceive:
            with self.assertRaises(KerberosError):
                getKerberosTGS(
                    Principal('cifs/server.example.com', type=constants.PrincipalNameType.NT_SRV_INST.value),
                    'EXAMPLE.COM',
                    None,
                    _build_rc4_tgt(),
                    _RC4Cipher(),
                    object(),
                    etypes=requestedEtypes,
                )

        sendReceive.assert_called_once()
        self.assertEqual(requests, [expectedEtypes])

    def test_default_tgs_enctypes_are_aes_first(self):
        self.assertEqual(
            getKerberosTGSRequestEnctypes(),
            (
                constants.EncryptionTypes.aes256_cts_hmac_sha1_96.value,
                constants.EncryptionTypes.aes128_cts_hmac_sha1_96.value,
                constants.EncryptionTypes.rc4_hmac.value,
                constants.EncryptionTypes.des3_cbc_sha1_kd.value,
                constants.EncryptionTypes.des_cbc_md5.value,
            ),
        )
        self.assertEqual(getKerberosTGSRequestEnctypes(), DEFAULT_TGS_ENCTYPES)

    def test_tgs_enctype_override_is_normalized(self):
        self.assertEqual(
            getKerberosTGSRequestEnctypes(
                (
                    constants.EncryptionTypes.rc4_hmac,
                    constants.EncryptionTypes.aes256_cts_hmac_sha1_96.value,
                )
            ),
            (
                constants.EncryptionTypes.rc4_hmac.value,
                constants.EncryptionTypes.aes256_cts_hmac_sha1_96.value,
            ),
        )

    def test_empty_tgs_enctype_override_is_rejected(self):
        with self.assertRaises(ValueError):
            getKerberosTGSRequestEnctypes(())

    def test_rc4_tgt_advertises_default_enctypes_in_one_request(self):
        self._assert_request_enctypes(None, DEFAULT_TGS_ENCTYPES)

    def test_rc4_preference_can_be_requested_explicitly(self):
        self._assert_request_enctypes(RC4_PREFERRED_TGS_ENCTYPES, RC4_PREFERRED_TGS_ENCTYPES)


class KerberosTGSRealmTests(TestCase):
    def _request_realm(self, domain, tgtService, ticketRealm='EXAMPLE.COM'):
        """Returns the realm of the emitted TGS-REQ and the host it was sent to"""
        sent = []

        def capture_request(data, host, kdcHost, timeout=None):
            tgsReq = decoder.decode(data, asn1Spec=TGS_REQ())[0]
            sent.append((str(tgsReq['req-body']['realm']), host))
            raise KerberosError(constants.ErrorCodes.KDC_ERR_S_PRINCIPAL_UNKNOWN.value)

        with mock.patch('impacket.krb5.kerberosv5.sendReceive', side_effect=capture_request):
            with self.assertRaises(KerberosError):
                getKerberosTGS(
                    Principal('cifs/server.child.example.com', type=constants.PrincipalNameType.NT_SRV_INST.value),
                    domain,
                    None,
                    _build_rc4_tgt(tgtService, ticketRealm),
                    _RC4Cipher(),
                    object(),
                )

        self.assertEqual(len(sent), 1)
        return sent[0]

    def test_regular_tgt_keeps_the_requested_realm(self):
        self.assertEqual(self._request_realm('EXAMPLE.COM', 'krbtgt/EXAMPLE.COM'),
                         ('EXAMPLE.COM', 'EXAMPLE.COM'))

    def test_inter_realm_tgt_is_sent_to_the_realm_it_grants(self):
        # krbtgt/CHILD.EXAMPLE.COM@EXAMPLE.COM can only be used at CHILD.EXAMPLE.COM's KDC,
        # asking EXAMPLE.COM's own KDC returns KDC_ERR_WRONG_REALM
        self.assertEqual(self._request_realm('EXAMPLE.COM', 'krbtgt/CHILD.EXAMPLE.COM'),
                         ('CHILD.EXAMPLE.COM', 'CHILD.EXAMPLE.COM'))
        self.assertEqual(self._request_realm('example.com', 'krbtgt/child.example.com'),
                         ('CHILD.EXAMPLE.COM', 'CHILD.EXAMPLE.COM'))

    def test_realm_explicitly_asked_by_the_caller_is_kept(self):
        # Referral chasing walks the trust path, the caller's realm must win there
        self.assertEqual(self._request_realm('OTHER.COM', 'krbtgt/CHILD.EXAMPLE.COM'),
                         ('OTHER.COM', 'OTHER.COM'))

    def test_service_ticket_used_as_a_tgt_keeps_the_requested_realm(self):
        self.assertEqual(self._request_realm('EXAMPLE.COM', 'cifs/server.example.com'),
                         ('EXAMPLE.COM', 'EXAMPLE.COM'))


class SendReceiveTests(TestCase):
    @staticmethod
    def _serve(behaviour):
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', 0))
        server.listen(1)

        def run():
            try:
                client, _ = server.accept()
            except OSError:
                return
            client.recv(4096)
            if behaviour == 'truncated_prefix':
                pass
            elif behaviour == 'truncated_body':
                client.sendall(struct.pack('!i', 500) + b'\x00' * 10)
            elif behaviour == 'negative_length':
                client.sendall(struct.pack('!i', -1))
            elif behaviour == 'silent':
                time.sleep(5)
            else:
                client.sendall(struct.pack('!i', 8) + b'\x00' * 8)
            client.close()

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
        return server, server.getsockname()[1], thread

    def _sendReceive(self, behaviour, timeout=None):
        server, port, _ = self._serve(behaviour)
        try:
            return sendReceive(b'\x00' * 32, 'EXAMPLE.COM', '127.0.0.1', port=port, timeout=timeout)
        finally:
            server.close()

    def test_answer_is_returned(self):
        self.assertEqual(self._sendReceive('answer'), b'\x00' * 8)

    def test_disconnect_before_length_prefix_is_reported(self):
        with self.assertRaises(socket.error) as caught:
            self._sendReceive('truncated_prefix')
        self.assertIn('0 of 4 bytes', str(caught.exception))

    def test_disconnect_inside_body_is_reported(self):
        # This used to spin forever on empty reads instead of failing.
        with self.assertRaises(socket.error) as caught:
            self._sendReceive('truncated_body')
        self.assertIn('10 of 500 bytes', str(caught.exception))

    def test_non_positive_length_is_reported(self):
        with self.assertRaises(socket.error) as caught:
            self._sendReceive('negative_length')
        self.assertIn('-1 byte answer', str(caught.exception))

    def test_timeout_covers_the_answer_not_just_the_connect(self):
        # The timeout used to be cleared after connect, so a silent KDC blocked forever.
        started = time.time()
        with self.assertRaises(socket.timeout):
            self._sendReceive('silent', timeout=1)
        self.assertLess(time.time() - started, 4)

    def test_socket_is_closed_after_the_exchange(self):
        server, port, thread = self._serve('answer')
        opened = []
        realSocket = socket.socket

        def tracking(*args, **kwargs):
            created = realSocket(*args, **kwargs)
            opened.append(created)
            return created

        try:
            # Tracks the accepted server side too, so wait for it before asserting.
            with mock.patch('socket.socket', side_effect=tracking):
                sendReceive(b'\x00' * 32, 'EXAMPLE.COM', '127.0.0.1', port=port)
                thread.join(5)
        finally:
            server.close()

        self.assertTrue(opened)
        for created in opened:
            self.assertEqual(created.fileno(), -1)
