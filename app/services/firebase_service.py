import firebase_admin
from firebase_admin import credentials, firestore

# A sua chave de serviço deve estar na raiz do projeto
SERVICE_ACCOUNT_KEY_PATH = "serviceAccountKey.json"

def get_firestore_client():
    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred)
    except ValueError:
        # O aplicativo já foi inicializado
        pass
    return firestore.client()