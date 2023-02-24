import requests
from datetime import datetime
import streamlit as st

# Función para leer los sitios web de un archivo de texto
def leer_webs():
    with open("web.txt", "r") as f:
        return [line.strip() for line in f.readlines()]

# Función para verificar el certificado SSL de un sitio web
def verificar_certificado(url):
    try:
        res = requests.get(url)
        expira = res.headers['Expires']
        expira = datetime.strptime(expira, '%a, %d %b %Y %H:%M:%S %Z')
        dias_restantes = (expira - datetime.now()).days
        return {
            'url': url,
            'expira_en': dias_restantes
        }
    except requests.exceptions.RequestException:
        return {
            'url': url,
            'expira_en': 'No se pudo verificar'
        }

if __name__ == '__main__':
    # Crear la aplicación Streamlit
    st.title("Verificación de certificados SSL")
    webs = leer_webs()
    resultados = []
    for web in webs:
        resultados.append(verificar_certificado(web))
    st.table(resultados)

