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

db = firestore.client()  # Inizializza Firestore

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
    if st.sidebar.button("Sei un giocatore?"):
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
                    st.session_state.user_email = email  # Salva l'email dell'utente
                    st.success(f'Benvenuto, {email}!')
                    st.toast('Hooray! good job, but now " + "DOUBLE CLICK".upper()', icon='🎉')
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
                    st.session_state.user_email = email  # Salva l'email dell'utente
                    
                    # Reindirizza alla pagina per inserire informazioni aggiuntive
                    st.session_state.page = "complete_profile"  # Cambia pagina a "complete_profile"
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

    # Nuova pagina per completare il profilo utente
    elif st.session_state.page == "complete_profile":
        st.title('Completa il tuo Profilo')
        st.markdown('### Inserisci le tue informazioni personali')

        first_name = st.text_input('Nome')
        last_name = st.text_input('Cognome')
        year_of_birth = st.number_input('Anno di nascita', min_value=1900, max_value=2024, step=1)

        if st.button('Salva Informazioni'):
            # Salva le informazioni nel Firestore
            db.collection('users').document(st.session_state.user_email).set({
                'first_name': first_name,
                'last_name': last_name,
                'year_of_birth': year_of_birth
            })
            st.success('Informazioni salvate con successo!')
            st.session_state.page = "user_profile"  # Cambia pagina al profilo utente

    # Nuova pagina per il profilo utente
    elif st.session_state.page == "user_profile":
        st.title('Profilo Utente')
        st.markdown('Ecco le tue informazioni.')

        # Recupera i dati dell'utente da Firestore
        user_doc = db.collection('users').document(st.session_state.user_email).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            first_name = st.text_input('Nome', value=user_data.get('first_name'), key='first_name')
            last_name = st.text_input('Cognome', value=user_data.get('last_name'), key='last_name')
            year_of_birth = st.number_input('Anno di nascita', min_value=1900, max_value=2024, step=1, value=user_data.get('year_of_birth'))

            if st.button('Aggiorna Informazioni'):
                # Aggiorna i dati nel Firestore
                db.collection('users').document(st.session_state.user_email).update({
                    'first_name': first_name,
                    'last_name': last_name,
                    'year_of_birth': year_of_birth
                })
                st.success('Informazioni aggiornate con successo!')
        else:
            st.warning('Nessuna informazione trovata.')  # Messaggio generico

if __name__ == '__main__':
    app()
