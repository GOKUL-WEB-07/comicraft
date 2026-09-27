const form = document.querySelector('#comic-form');
if (form) {
  form.addEventListener('submit', () => {
    if (!form.checkValidity()) return;
    const button = document.querySelector('#submit-button');
    const loading = document.querySelector('#loading');
    const message = document.querySelector('#loading-message');
    const messages = ['Writing the story...', 'Designing comic panels...', 'Creating illustrations...', 'Preparing your comic...'];
    button.disabled = true;
    loading.hidden = false;
    let index = 0;
    window.setInterval(() => { index = Math.min(index + 1, messages.length - 1); message.textContent = messages[index]; }, 3500);
  });
}
