const resetPswdForm = document.getElementById('reset-pswd-form');
const pathForReset = window.location.pathname;
const msg = document.querySelector('.message');
console.log(pathForReset);
let response;
resetPswdForm.addEventListener('submit', async(e) => {
  e.preventDefault();
  const data = {}
  data['pswd'] = document.querySelector("#pswd").value;
  data['pswd-cnfrm'] = document.querySelector("#pswd-cnfrm").value;
  response = await fetch(pathForReset, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
    'Content-Type': 'application/json'
    },
  });
  const result = await response.json();
  console.log(response);
  console.log(result);
  switch (response.status) {
    case 400:
      msg.textContent = result;
      break;
    case 403:
      msg.innerHTML = "<span>Invalid or expired token. Please <a href='/forgotpassword'>get a new token</a>.";
      break;
    case 200:
      window.location.replace(window.location.origin + '/password_changed')
      break
    default:
      throw new Exception('Unexpected error');
  }
})
