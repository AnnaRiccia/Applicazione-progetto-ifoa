import streamlit as st
import firebase_admin
import requests
from firebase_admin import credentials, auth, firestore
import os

# Ottieni le credenziali di Firebase dall'ambiente
firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
cred = credentials.Certificate(eval(firebase_credentials))

# Inizializza Firebase solo se non è già stato fatto
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

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
    return response.json()


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
    if st.sidebar.button("Devi registrarti?"):
        st.session_state.page = "login_signup"

    # Pagina principale
    if st.session_state.get('page', 'home') == "home":
        st.title('Registrazione')
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
                    st.session_state.user_email = email  # Salva l'email dell'utente
                    st.success(f'Benvenuto, {email}!')
                    st.markdown(
                        """
                        <div style="position: fixed; bottom: 170px; left: 50%; transform: translateX(-50%); background-color: #90EE90; color: black; padding: 10px 20px; border-radius: 5px; text-align: center;">
                        🎉 Bentornato!
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.write("<div style='height: 50px;'></div>", unsafe_allow_html=True)
                    st.session_state.page = "user_profile"  # Passa alla pagina del profilo
                else:
                    st.warning('Credenziali errate. Riprova.')

        # Sezione Sign Up
        elif selezione == 'Sign Up':
            st.markdown('### Registrati qui')
            email = st.text_input('Indirizzo Email (Registrazione)')
            password = st.text_input('Password (Registrazione)', type='password')
            if st.button('Crea Account'):
                try:
                    # Crea un nuovo utente con email e password
                    user = auth.create_user(email=email, password=password)
                    st.success('Account creato con successo!')
                    st.markdown(
                        """
                        <div style="position: fixed; bottom: 170px; left: 50%; transform: translateX(-50%); background-color: #90EE90; color: black; padding: 10px 20px; border-radius: 5px; text-align: center;">
                        🎉 Account creato con successo
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.write("<div style='height: 50px;'></div>", unsafe_allow_html=True)
                    st.session_state.user_email = email  # Salva l'email dell'utente
                except Exception as e:
                    st.warning('Creazione account fallita. Riprova.')  # Messaggio generico

        # Sezione Recupera password
        elif selezione == 'Recupera password':
            st.markdown('## Recupera la tua password')
            reset_email = st.text_input('Inserisci il tuo indirizzo email per il recupero')
            if st.button('Invia Richiesta di Recupero'):
                response = send_password_reset(reset_email)
                if 'error' not in response:
                    st.success('Email di recupero inviata con successo! Controlla la tua casella email.')
                else:
                    st.warning('Invio della richiesta di recupero fallito. Riprova.')  # Messaggio generico

# Avvia l'app
if __name__ == '__main__':
    app()