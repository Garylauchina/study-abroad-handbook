// Material observes keyup. Also refresh for paste, autofill and Chinese IME input.
(() => {
  const query = document.querySelector('[data-md-component="search-query"]');
  if (!query) return;
  const refresh = () => query.dispatchEvent(new KeyboardEvent('keyup', {
    key: 'Unidentified', bubbles: true,
  }));
  query.addEventListener('input', event => { if (!event.isComposing) refresh(); });
  query.addEventListener('compositionend', refresh);
  query.form.addEventListener('reset', () => queueMicrotask(refresh));
})();
