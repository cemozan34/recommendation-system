Array.prototype.slice.call(document.querySelectorAll('.toggle-fav-btn')).forEach((btn) => {
  btn.addEventListener('click', async(e) => {
    e.preventDefault();
    console.log(btn.dataset.href);
    try {
      const response = await fetch(btn.dataset.href);
      await response.json();
      // btn.firstElementChild.classList.toggle('isFilled');
      const img = btn.firstElementChild;
      if (img.src.endsWith('heart-filled.png')) {
        console.log('removed from favs');
        img.src = "../static/heart-empty.png";
        img.alt = "Add to favorites";
      } else {
        console.log('added to favs');
        img.src = "../static/heart-filled.png";
        img.alt = "Remove from favorites";
      }
    } catch (error) {
      console.log("Couldn't toggle the fav")
      console.log(error);
    }
  })
})
