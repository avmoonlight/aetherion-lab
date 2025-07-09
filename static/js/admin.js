// admin.js

function openPopup(contentId) {
  document.getElementById(contentId).style.display = 'flex';
}

function closePopup(contentId) {
  document.getElementById(contentId).style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.popup-close').forEach(closeBtn => {
    closeBtn.addEventListener('click', () => {
      closePopup(closeBtn.closest('.popup').id);
    });
  });

  document.querySelectorAll('.btn-add, .btn-edit, .btn-delete').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-target');
      openPopup(target);
    });
  });
});
