import ssl
import socket
from datetime import datetime
import streamlit as st
import OpenSSL.crypto

# Función para verificar el certificado SSL de un sitio web
def verificar_certificado(url):
    try:
        cert = ssl.get_server_certificate((url, 443))
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
        expira = x509.get_notAfter().decode("ascii")
        expira = datetime.strptime(expira, '%Y%m%d%H%M%SZ')
        dias_restantes = (expira - datetime.now()).days
        return {
            'url': url,
            'expira_en': dias_restantes
        }
    except (ssl.CertificateError, ssl.SSLError, socket.gaierror):
        return {
            'url': url,
            'expira_en': 'No se pudo verificar'
        }

# Configurar la aplicación Streamlit
st.set_page_config(page_title='SSL Checker')

# Mostrar un formulario para ingresar la URL
st.title('SSL Checker')
url = st.text_input('Ingrese la URL del sitio web a verificar')

# Verificar el certificado SSL y mostrar los resultados en una tabla
if url:
    st.write('Verificando el certificado SSL para:', url)
    resultado = verificar_certificado(url)
    st.write('El certificado SSL para', url, 'expira en', resultado['expira_en'], 'días')
    st.write('Resultados:')
    st.table([resultado])


