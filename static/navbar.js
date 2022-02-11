const path = window.location.pathname;
const changePass = document.getElementById('change-password')
if (path !== '/' && changePass) {
  changePass.style.display = 'none';
}
