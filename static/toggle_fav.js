Array.prototype.slice.call(document.querySelectorAll('.toggle-fav-btn')).forEach((btn) => {
  btn.addEventListener('click', async(e) => {
    e.preventDefault();
    console.log(btn.dataset.href);
    try {
      const response = await fetch(btn.dataset.href);
      const json = await response.json();
      btn.firstElementChild.classList.toggle('isFilled');
      console.log(json);
    } catch (error) {
      console.log("Couldn't toggle the fav")
      console.log(error);
    }
  })
})
