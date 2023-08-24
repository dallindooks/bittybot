class FooterComponent extends HTMLElement {
    constructor() {
      super();
      const shadow = this.attachShadow({ mode: "open" });
  
      fetch("components/footer/footer-component.html")
        .then((response) => response.text())
        .then((content) => {
          const template = document.createElement("template");
          template.innerHTML = content;
          shadow.appendChild(template.content.cloneNode(true));
        })
        .catch((error) => {
          console.error("Error loading footer-component.html:", error);
        });
        
    }
  }
  
  customElements.define("footer-component", FooterComponent);