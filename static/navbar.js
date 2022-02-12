const path = window.location.pathname;
const changePass = document.getElementById('change-password')
if (changePass && !path.match(/\/([0-9]*|favorites)$/)) {
  changePass.style.display = 'none';
}
