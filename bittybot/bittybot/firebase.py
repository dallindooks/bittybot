import pyrebase
import os

config = {
  "apiKey": "AIzaSyClIzSDGqO-TK2CQxwqXJ0Oas84o4IOKRc",
  "authDomain": "bittybot-778dc.firebaseapp.com",
  "projectId": "bittybot-778dc",
  "storageBucket": "bittybot-778dc.appspot.com",
  "messagingSenderId": "376729658832",
  "appId": "1:376729658832:web:9410aa9542222b6beac5d5",
  "measurementId": "G-X35MWPZPPN"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()