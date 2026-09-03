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
