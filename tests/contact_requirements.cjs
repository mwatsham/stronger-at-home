const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

// Exercise the production controller with a minimal DOM boundary, without a browser or network.
function setup(preference = 'email') {
  const field = value => ({
    value, required: false, textContent: '', handlers: {}, validity: {valid: true},
    setCustomValidity(message) { this.validationMessage = message; },
    removeAttribute() {}, addEventListener(name, fn) { this.handlers[name] = fn; },
  });
  const email = field('reader@example.test');
  const phone = field('07700 900123');
  const preferred = field(preference);
  const emailRequirement = field('');
  const phoneRequirement = field('');
  const status = {dataset: {}, textContent: ''};
  const nodes = {'#email': email, '#phone': phone, '#preferred-contact': preferred,
    '#email-requirement': emailRequirement, '#phone-requirement': phoneRequirement,
    '[data-form-status]': status};
  const form = {querySelector: selector => nodes[selector] || null, addEventListener() {}};
  const document = {documentElement: {classList: {add() {}}},
    querySelector: selector => selector === 'form.appointment-form' ? form : null};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../site/assets/js/site.js'), 'utf8'), {document});
  return {email, phone, preferred, emailRequirement, phoneRequirement};
}
for (const initial of ['email', 'phone']) {
  const state = setup(initial);
  for (const choice of [initial, 'phone', 'email']) {
    state.preferred.value = choice;
    state.preferred.handlers.change({target: state.preferred});
    assert.equal(state.email.required, choice === 'email');
    assert.equal(state.phone.required, choice === 'phone');
    assert.equal(state.emailRequirement.textContent, choice === 'email' ? '(required)' : '(optional)');
    assert.equal(state.phoneRequirement.textContent, choice === 'phone' ? '(required)' : '(optional)');
    assert.equal(state.email.value, 'reader@example.test');
    assert.equal(state.phone.value, '07700 900123');
  }
}
const initial = setup();
assert.equal(initial.email.required, true, 'Email requirement must be set on first load');
assert.equal(initial.phone.required, false);
console.log('Contact preference behavior passed');
