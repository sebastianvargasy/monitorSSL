import pandas as pd
from OpenSSL import SSL
from cryptography import x509
from cryptography.x509.oid import NameOID
import idna
import streamlit as st

from socket import socket
from collections import namedtuple

HostInfo = namedtuple(field_names='cert hostname peername', typename='HostInfo')

HOSTS = [
    ('damjan.softver.org.mk', 443),
    ('expired.badssl.com', 443),
    ('wrong.host.badssl.com', 443),
    ('ca.ocsr.nl', 443),
    ('faß.de', 443),
    ('самодеј.мкд', 443),
]

def verify_cert(cert, hostname):
    # verify notAfter/notBefore, CA trusted, servername/sni/hostname
    cert.has_expired()
    # service_identity.pyopenssl.verify_hostname(client_ssl, hostname)
    # issuer

def get_certificate(hostname, port):
    hostname_idna = idna.encode(hostname)
    sock = socket()

    sock.connect((hostname, port))
    peername = sock.getpeername()
    ctx = SSL.Context(SSL.SSLv23_METHOD) # most compatible
    ctx.check_hostname = False
    ctx.verify_mode = SSL.VERIFY_NONE

    sock_ssl = SSL.Connection(ctx, sock)
    sock_ssl.set_connect_state()
    sock_ssl.set_tlsext_host_name(hostname_idna)
    sock_ssl.do_handshake()
    cert = sock_ssl.get_peer_certificate()
    crypto_cert = cert.to_cryptography()
    sock_ssl.close()
    sock.close()

    return HostInfo(cert=crypto_cert, peername=peername, hostname=hostname)

def get_alt_names(cert):
    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        return ext.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        return None

def get_common_name(cert):
    try:
        names = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        return names[0].value
    except x509.ExtensionNotFound:
        return None

def get_issuer(cert):
    try:
        names = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
        return names[0].value
    except x509.ExtensionNotFound:
        return None


def get_basic_info(hostinfo):
    s = {
        'hostname': hostinfo.hostname,
        'peername': hostinfo.peername,
        'commonname': get_common_name(hostinfo.cert),
        'SAN': get_alt_names(hostinfo.cert),
        'issuer': get_issuer(hostinfo.cert),
        'notbefore': hostinfo.cert.not_valid_before,
        'notafter': hostinfo.cert.not_valid_after
    }
    return s

if __name__ == '__main__':
    # Crear la aplicación Streamlit
    st.title("Verificación de certificados SSL")
    resultados = []
    for host in HOSTS:
        hostinfo = get_certificate(host[0], host[1])
        resultados.append(get_basic_info(hostinfo))
    df = pd.DataFrame(resultados)
    st.dataframe(df)

