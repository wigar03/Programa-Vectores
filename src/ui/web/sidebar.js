/* Navegación lateral: conserva los selectores y eventos de los módulos existentes. */
document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("module-sidebar");
  const toggle = document.getElementById("btn-nav-toggle");
  const close = document.getElementById("btn-nav-close");
  const backdrop = document.getElementById("sidebar-backdrop");
  const tabs = [...sidebar.querySelectorAll(".nav-tab")];
  const mobile = window.matchMedia("(max-width: 900px)");

  function seleccionar() {
    tabs.forEach(tab => {
      if (tab.classList.contains("active")) tab.setAttribute("aria-current", "page");
      else tab.removeAttribute("aria-current");
    });
  }

  function abrir(abierto, devolverFoco = true) {
    const visible = abierto && mobile.matches;
    document.body.classList.toggle("sidebar-open", visible);
    toggle.setAttribute("aria-expanded", String(visible));
    sidebar.setAttribute("aria-hidden", String(mobile.matches && !visible));
    backdrop.hidden = !visible;
    if (visible) (sidebar.querySelector(".nav-tab.active") || close).focus();
    else if (devolverFoco && mobile.matches) toggle.focus();
  }

  toggle.addEventListener("click", () => abrir(!document.body.classList.contains("sidebar-open")));
  close.addEventListener("click", () => abrir(false));
  backdrop.addEventListener("click", () => abrir(false));
  document.addEventListener("calculator:navigate", evento => {
    seleccionar();
    abrir(false, false);
    const destino = document.getElementById(evento.detail.targetId);
    destino.setAttribute("tabindex", "-1");
    destino.focus({ preventScroll: true });
    destino.scrollIntoView?.({ block: "start" });
  });
  document.addEventListener("keydown", evento => {
    if (!mobile.matches || !document.body.classList.contains("sidebar-open")) return;
    if (evento.key === "Escape") { evento.preventDefault(); abrir(false); }
    if (evento.key === "Tab") {
      const focos = [close, ...tabs];
      const primero = focos[0], ultimo = focos[focos.length - 1];
      if (evento.shiftKey && document.activeElement === primero) {
        evento.preventDefault(); ultimo.focus();
      } else if (!evento.shiftKey && document.activeElement === ultimo) {
        evento.preventDefault(); primero.focus();
      }
    }
  });
  mobile.addEventListener("change", () => abrir(false, false));
  seleccionar();
  abrir(false, false);
});
