class LoginComponent extends HTMLElement {
  constructor() {
    super();
    const shadow = this.attachShadow({ mode: "open" });
    fetch("components/login/login-component.html")
      .then((response) => response.text())
      .then((content) => {
        const template = document.createElement("template");
        template.innerHTML = content;

        let loginButton = template.content.querySelector("#google-login-button")
        console.log(loginButton)
        loginButton.addEventListener("click", () => {
          window.location.href = "dashboard.html";
        });

        shadow.appendChild(template.content.cloneNode(true));
      })
      .catch((error) => {
        console.error("Error loading login-component.html:", error);
      });
  }

}

customElements.define("login-component", LoginComponent);
