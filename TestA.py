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
                    st.session_state.user_email = email  # Salva l'email dell'utente
                    st.success(f'Benvenuto, {email}!')
                    st.session_state.page = "user_profile"  # Passa alla pagina del profilo
                    st.experimental_rerun()  # Ricarica per mostrare la nuova pagina
                else:
                    error_message = response.get('error', {}).get('message', 'Errore di autenticazione')
                    st.error(f'Login fallito: {error_message}')

        # Sezione Sign Up
        elif selezione == 'Sign Up':
            st.session_state.page = "signup_email"  # Cambia a una nuova pagina per la registrazione dell'email
            st.rerun()  # Ricarica l'app per visualizzare la nuova pagina

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

    # Nuova pagina per la registrazione dell'email
    elif st.session_state.page == "signup_email":
        st.title('Registrazione Nuovo Utente')
        st.markdown('Compila i campi sottostanti per completare la registrazione.')

        email = st.text_input('Indirizzo Email (Registrazione)')
        password = st.text_input('Password (Registrazione)', type='password')
        if st.button('Crea Account'):
            try:
                # Crea un nuovo utente con email e password
                user = auth.create_user(email=email, password=password)
                st.success('Account creato con successo!')

                # Passa alla pagina successiva per inserire nome, cognome e data di nascita
                st.session_state.page = "signup_details"
                st.experimental_rerun()  # Ricarica per mostrare la nuova pagina

            except Exception as e:
                st.error('Creazione account fallita: ' + str(e))

    # Nuova pagina per inserire nome, cognome e anno di nascita
    elif st.session_state.page == "signup_details":
        st.title('Completa la Registrazione')
        st.markdown('Compila i campi sottostanti per completare il profilo.')

        first_name = st.text_input('Nome')
        last_name = st.text_input('Cognome')
        year_of_birth = st.number_input('Anno di nascita', min_value=1900, max_value=2024, step=1)

        if st.button('Completa Registrazione'):
            # Salva le informazioni nel Firestore
            user_doc = {
                'first_name': first_name,
                'last_name': last_name,
                'year_of_birth': year_of_birth,
                'email': st.session_state.user_email  # Usa l'email salvata
            }

            # Salva i dati dell'utente in Firestore
            db.collection('users').document(st.session_state.user_email).set(user_doc)
            st.success('Registrazione completata con successo!')

            st.session_state.page = "home"  # Torna alla pagina principale dopo la registrazione
            st.experimental_rerun()  # Ricarica per mostrare la pagina principale

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
            st.error('Nessuna informazione trovata.')

if __name__ == '__main__':
    app()
