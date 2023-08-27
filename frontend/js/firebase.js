import { initializeApp } from "https://www.gstatic.com/firebasejs/10.3.0/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/10.3.0/firebase-auth.js"; 
import { getDatabase } from "https://www.gstatic.com/firebasejs/10.3.0/firebase-database.js"


const firebaseConfig = {
  apiKey: "AIzaSyClIzSDGqO-TK2CQxwqXJ0Oas84o4IOKRc",
  authDomain: "bittybot-778dc.firebaseapp.com",
  databaseURL: "https://bittybot-778dc-default-rtdb.firebaseio.com",
  projectId: "bittybot-778dc",
  storageBucket: "bittybot-778dc.appspot.com",
  messagingSenderId: "376729658832",
  appId: "1:376729658832:web:9410aa9542222b6beac5d5",
  measurementId: "G-X35MWPZPPN"
};

const firebase = initializeApp(firebaseConfig)
const db = getDatabase(firebase);

export const auth = getAuth();
export const provider = new GoogleAuthProvider();
export { firebase, db }

