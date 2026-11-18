import { withViewTransition } from '../dist/syntyr.animate.mjs';

const list = document.querySelector('#record-list');
const status = document.querySelector('#motion-message');
let nextRecord = 3;

document.querySelector('#add-record').addEventListener('click', () => {
  const article = document.createElement('article');
  article.className = 'syn-panel';
  article.dataset.synMotion = 'insert';
  article.style.viewTransitionName = 'syn-record-' + nextRecord;
  article.textContent = 'Campaign ' + nextRecord + ' — new record';
  nextRecord += 1;
  list.append(article);
  status.textContent = 'A new campaign record was added.';
});

document.querySelector('#reorder-records').addEventListener('click', () => {
  withViewTransition(() => {
    list.replaceChildren(...Array.from(list.children).reverse());
  });
  status.textContent = 'Campaign records reordered.';
});

document.querySelector('#send-notice').addEventListener('click', () => {
  const notice = document.createElement('p');
  notice.className = 'syn-panel';
  notice.dataset.synMotion = 'notice';
  notice.textContent = 'The invoice has been sent successfully.';
  document.querySelector('#notice-container').replaceChildren(notice);
  status.textContent = 'Invoice sent successfully.';
});

document.querySelector('#save-record').addEventListener('click', (event) => {
  const button = event.currentTarget;
  button.dataset.synMotion = 'saved';
  button.textContent = 'Saved';
  status.textContent = 'Changes saved successfully.';
});
