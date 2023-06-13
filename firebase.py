import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(
    "./flatmap-90f33-firebase-adminsdk-i2t5z-dbfe07f578.json")

app = firebase_admin.initialize_app(cred)
db = firestore.client()

def user_creation(userid):
    doc_ref = db.collection('users').document(userid)
    if not doc_ref.get().to_dict():
        data = {'liked_flats': []}
        doc_ref.set(data)
    return


def add_liked_to_database(userid, liked_info):
    doc_ref = db.collection('users').document(userid)
    doc = doc_ref.get()

    info_list = doc.to_dict().get('liked_flats')
    # Добавьте новые данные в массив
    info_list.append(liked_info)
    # Обновите документ пользователя, включая новые данные
    doc_ref.update({'liked_flats': info_list})

    print("Succesfully added")
    return


def get_liked_from_database(userid):
    doc_ref = db.collection('users').document(userid)
    doc = doc_ref.get()

    flats = doc.to_dict().get('liked_flats')

    return flats
