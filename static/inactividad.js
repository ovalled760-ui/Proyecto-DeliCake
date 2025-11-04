// static/js/inactividad.js
(function() {
  const TIEMPO_INACTIVIDAD_MS = 60 * 1000; // 1 minuto
  const CUENTA_ATRAS_SEG = 10;             // segundos de aviso
  const REDIRECT_URL = window.INACTIVITY_REDIRECT || '/';

  if (window.NO_INACTIVITY_MODAL) return;

  let modal = document.getElementById('modal-inactividad-js');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'modal-inactividad-js';
    modal.innerHTML = `
      <div class="modal-inactividad__backdrop">
        <div class="modal-inactividad__box" role="dialog" aria-modal="true" aria-labelledby="modal-inactividad-title">
          <h3 id="modal-inactividad-title">💤 Inactividad detectada</h3>
          <p>Serás redirigido al inicio en <strong><span id="modal-inactividad-contador">${CUENTA_ATRAS_SEG}</span>s</strong>.</p>
          <div class="modal-inactividad__controls">
            <button id="modal-inactividad-cancel" class="btn-coquette">Seguir aquí 🎀</button>
            <button id="modal-inactividad-go" class="btn-link">Ir al inicio</button>
          </div>
        </div>
      </div>`;
    document.body.appendChild(modal);
  }

  const backdrop = modal.querySelector('.modal-inactividad__backdrop');
  const contadorSpan = modal.querySelector('#modal-inactividad-contador');
  const btnCancelar = modal.querySelector('#modal-inactividad-cancel');
  const btnGo = modal.querySelector('#modal-inactividad-go');

  let inactivityTimer = null;
  let countdownInterval = null;

  function showModalAndStartCountdown() {
    backdrop.style.display = 'flex';
    let seg = CUENTA_ATRAS_SEG;
    contadorSpan.textContent = seg;
    countdownInterval = setInterval(() => {
      seg--;
      contadorSpan.textContent = seg;
      if (seg <= 0) {
        clearInterval(countdownInterval);
        window.location.href = REDIRECT_URL;
      }
    }, 1000);
  }

  function hideModalAndRestart() {
    backdrop.style.display = 'none';
    if (countdownInterval) {
      clearInterval(countdownInterval);
      countdownInterval = null;
    }
    restartInactivityTimer();
  }

  function restartInactivityTimer() {
    if (inactivityTimer) clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(showModalAndStartCountdown, TIEMPO_INACTIVIDAD_MS);
  }

  const events = ['mousemove','keydown','click','scroll','touchstart'];
  events.forEach(e => document.addEventListener(e, restartInactivityTimer, {passive:true}));

  btnCancelar.addEventListener('click', hideModalAndRestart);
  btnGo.addEventListener('click', () => { window.location.href = REDIRECT_URL; });

  restartInactivityTimer();

  document.addEventListener('focusin', (ev) => {
    const t = ev.target;
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) {
      if (inactivityTimer) clearTimeout(inactivityTimer);
    }
  });
  document.addEventListener('focusout', () => {
    restartInactivityTimer();
  });
})();
