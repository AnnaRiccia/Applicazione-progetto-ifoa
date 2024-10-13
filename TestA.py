import streamlit as st
import firebase_admin
import requests
from firebase_admin import credentials, auth

# Percorso del file delle credenziali
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
    print(result)  # Stampa il risultato per il debug
    return result

def app():
    # Finestra laterale a sinistra
    st.sidebar.title("Menu")
    
    # Pulsante "HOME"
    if st.sidebar.button("HOME"):
        st.session_state.page = "home"  # Imposta la pagina a HOME

    # Pulsante "Sei un giocatore?"
    if st.sidebar.button("Sei un giocatore?"):
        if st.session_state.get('page', 'home') == "login_signup":
            st.session_state.page = "home"  # Torna a HOME se già su login_signup
        else:
            st.session_state.page = "login_signup"  # Imposta la pagina a login/signup

    # Pagina principale
    if st.session_state.get('page', 'home') == "home":
        st.title('Modigliana Calcio')  # Scritta principale
        st.markdown('applicazione in cantiere!')  # Messaggio di benvenuto
        st.markdown('Questa è la pagina principale. Puoi navigare per accedere o registrarti.')
    
    # Sezione di login/signup
    elif st.session_state.page == "login_signup":
        selezione = st.selectbox('Login/Signup', ['Login', 'Sign Up'])

        if selezione == 'Login':
            email = st.text_input('Indirizzo Email')
            password = st.text_input('Password', type='password')

            if st.button('Login'):
                response = authenticate_user(email, password)
                if 'idToken' in response:
                    st.success(f'Benvenuto, {email}!')
                else:
                    error_message = response.get('error', {}).get('message', 'Errore di autenticazione')
                    st.error(f'Login fallito: {error_message}')

        elif selezione == 'Sign Up':  # Sezione di registrazione
            email = st.text_input('Indirizzo Email (Registrazione)')
            password = st.text_input('Password (Registrazione)', type='password')

            if st.button('Crea Account'):
                try:
                    user = auth.create_user(email=email, password=password)
                    st.success('Account creato con successo!')
                    st.markdown('Accedere con email e password')
                except Exception as e:
                    st.error('Creazione account fallita: ' + str(e))

if __name__ == '__main__':
    app()
