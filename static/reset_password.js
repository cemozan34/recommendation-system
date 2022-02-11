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
  msg.textContent = result;
  switch (response.status) {
    case 400:
      msg.style.color = 'red';
      break;
    case 403:
      msg.style.color = 'red';
      resetPswdForm.style.display = 'none';
      document.querySelector('.forgot-pswd-ref').style.display = 'block';
      break;
    case 200:
      msg.style.color = 'darkgreen';
      resetPswdForm.style.display = 'none';
      document.querySelector('.login-ref').style.display = 'block';
      break
    default:
      throw new Exception('Unexpected error');
  }
})
