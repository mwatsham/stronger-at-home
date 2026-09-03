document.documentElement.classList.add('js');

const button = document.querySelector('.menu-button');
const navigation = document.querySelector('#primary-navigation');
if (button && navigation) {
  button.addEventListener('click', () => {
    const expanded = button.getAttribute('aria-expanded') === 'true';
    button.setAttribute('aria-expanded', String(!expanded));
    navigation.dataset.open = String(!expanded);
  });
}

const form = document.querySelector('#appointment-request');
if (form) {
  const email = form.querySelector('#email');
  const phone = form.querySelector('#phone');
  const preferredContact = form.querySelector('#preferred-contact');
  const status = form.querySelector('[data-form-status]');

  const updateContactRequirements = () => {
    const prefersEmail = preferredContact.value === 'email';
    const prefersPhone = preferredContact.value === 'phone';
    email.setCustomValidity(prefersEmail && !email.value.trim() ? 'Please provide an email address.' : '');
    phone.setCustomValidity(prefersPhone && !phone.value.trim() ? 'Please provide a phone number.' : '');
    [email, phone].forEach(field => {
      if (field.validity.valid) field.removeAttribute('aria-invalid');
    });
  };

  const clearStatusWhenFormIsValid = () => {
    if (!form.querySelector(':invalid')) {
      status.textContent = '';
    }
  };

  form.addEventListener('invalid', event => event.target.setAttribute('aria-invalid', 'true'), true);
  form.addEventListener('input', event => {
    event.target.removeAttribute('aria-invalid');
    updateContactRequirements();
    clearStatusWhenFormIsValid();
  });
  preferredContact.addEventListener('change', event => {
    event.target.removeAttribute('aria-invalid');
    updateContactRequirements();
    clearStatusWhenFormIsValid();
  });
  form.addEventListener('submit', event => {
    updateContactRequirements();
    if (!form.checkValidity()) {
      event.preventDefault();
      status.textContent = 'Please check the highlighted fields before sending your appointment request.';
      form.reportValidity();
    }
  });
}
