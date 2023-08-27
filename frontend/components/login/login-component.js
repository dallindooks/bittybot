import { firebase, auth, provider } from "../../js/firebase.js"
import { getAuth, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/10.3.0/firebase-auth.js";

const fetch_template = fetch("components/login/login-component.html")
  .then((response) => response.text())
  .then((content) => {
    const html = document.createElement("template");
    html.innerHTML = content;
    return html;
  })
  .catch((error) => {
    console.error("Error loading login-component.html:", error);
  });

fetch_template.then((template) => {

  class LoginComponent extends HTMLElement {
    constructor() {
      super();
      const shadow = this.attachShadow({ mode: "open" });
      shadow.append(template.content.cloneNode(true));
      this.shadowRoot.addEventListener("click", (event) => {
        if (event.target.matches("#google-login-button")) {
          this.signInWithGoogle()
        }
      });
    }

    signInWithGoogle() {
      console.log(provider)
      auth.languageCode = 'it';
      signInWithPopup(auth, provider)
        .then((result) => {
          const idToken = result.credential.idToken; // Get the ID token
          sendIdTokenToServer(idToken);
          var user = result.user;
          console.log("Signed in user:", user);
          window.location.href = "dashboard.html"
        })
        .catch((error) => {
          console.error("Authentication error:", error);
        });
    }

  }

  customElements.define("login-component", LoginComponent);
});

