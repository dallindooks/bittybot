import { firebase, auth, provider } from "./firebase.js"


auth.onAuthStateChanged(function(user) {

    console.log("this ran")
    if (user) {
      // User is signed in, redirect to a specific page
      window.location.href = "dashboard.html";
    } 
  });