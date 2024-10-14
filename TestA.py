import streamlit as st
import firebase_admin
import requests
from firebase_admin import credentials, auth
import os


firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
cred = credentials.Certificate(eval(firebase_credentials))

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
    return result

# Funzione per inviare una email di recupero password
def send_password_reset(email):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }
    response = requests.post(url, json=payload)
    result = response.json()
    if 'error' in result:
        return {"error": result['error']['message']}
    return result

def app():
    # Finestra laterale
    st.sidebar.title("Menu")
    
    # Pulsante "HOME"
    if st.sidebar.button("HOME"):
        st.session_state.page = "home"

    # Pulsante "Sei un giocatore?"
    if st.sidebar.button("Sei un giocatore?"):
        if st.session_state.get('page', 'home') == "login_signup":
            st.session_state.page = "home"
        else:
            st.session_state.page = "login_signup"

    # Pagina principale
    if st.session_state.get('page', 'home') == "home":
        st.title('Modigliana Calcio')
        st.markdown('Applicazione in cantiere!')
        st.markdown('Questa è la pagina principale. Puoi navigare per accedere o registrarti.')

    # Sezione di login/signup/recupero password
    elif st.session_state.page == "login_signup":
        st.title('Modigliana Calcio')
        selezione = st.selectbox('Login/Signup', ['Login', 'Sign Up', 'Recupera password'])

        # Sezione Login
        if selezione == 'Login':
            st.markdown('## Sei già registrato?')
            email = st.text_input('Indirizzo Email')
            password = st.text_input('Password', type='password')
            if st.button('Login'):
                response = authenticate_user(email, password)
                if 'idToken' in response:
                    st.success(f'Benvenuto, {email}!')
                else:
                    error_message = response.get('error', {}).get('message', 'Errore di autenticazione')
                    st.error(f'Login fallito: {error_message}')

        # Sezione Sign Up
        elif selezione == 'Sign Up':
            st.markdown('## Crea le tue credenziali!')
            email = st.text_input('Indirizzo Email (Registrazione)')
            password = st.text_input('Password (Registrazione)', type='password')
            if st.button('Crea Account'):
                try:
                    user = auth.create_user(email=email, password=password)
                    st.success('Account creato con successo!')
                    st.markdown('Accedere con email e password')
                except Exception as e:
                    st.error('Creazione account fallita: ' + str(e))

        # Sezione Recupera password
        elif selezione == 'Recupera password':
            st.markdown('## Recupera la tua password')
            reset_email = st.text_input('Inserisci il tuo indirizzo email per il recupero')
            if st.button('Invia Richiesta di Recupero'):
                response = send_password_reset(reset_email)
                if 'error' not in response:
                    st.success('Email di recupero inviata con successo! Controlla la tua casella email.')
                else:
                    st.error(f'Recupero password fallito: {response["error"]}')

if __name__ == '__main__':
    app()

