import streamlit as st
import firebase_admin
import requests
from firebase_admin import credentials, auth
import os
# Percorso del file delle credenziali

firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
cred = credentials.Certificate(eval(firebase_credentials))
# Il metodo eval() viene utilizzato 
# per convertire il contenuto della stringa JSON in un dizionario.

# Inizializza Firebase solo se non è già stato fatto
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Inserisci qui la tua Firebase API Key direttamente
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')

# Funzione per autenticare l'utente con email e password tramite la REST API di Firebase
def authenticate_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    result = response.json()
    print(result)  # Stampa il risultato per il debug
    return result

def app():
    st.title('Prova')
    selezione = st.selectbox('Login/Signup', ['Login', 'Sign Up'])
    
    if selezione == 'Login':
        email = st.text_input('Indirizzo Email')
        password = st.text_input('Password', type='password')
        
        if st.button('Login'):
            # Usa authenticate_user per verificare l'email e la password
            response = authenticate_user(email, password)
            if 'idToken' in response:
                st.success(f'Benvenuto, {email}!')
            else:
                error_message = response.get('error', {}).get('message', 'Errore di autenticazione')
                st.error(f'Login fallito: {error_message}')
                
    else:
        username = st.text_input('Inserisci nome utente')
        email = st.text_input('Indirizzo Email')
        password = st.text_input('Password', type='password')
        
        if st.button('Crea Account'):
            try:
                user = auth.create_user(email=email, password=password)
                st.success('Account creato con successo!')
                st.markdown('Accedere con email e password')
            except Exception as e:
                st.error('Creazione account fallita: ' + str(e))

if __name__ == '__main__':
    app()
