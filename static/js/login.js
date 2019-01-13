$(document).ready(() => {
  $("#submit").click(() => {
    if ($("#username").val() === '' || $("#password").val() === '') {
      alert("You have to have a username!")
      $("form").submit((event) => {
        event.preventDefault();
        event.stopPropagation();
      })
    }
    else {
      const para = { 
        username: $("#username").val(), 
        password: $("#password").val() 
      }
      $.post("/login", para, (data) => {
        if (data[0] === '/')
          window.location.replace(data)
        else
          alert(data)
      })
    }
  })
})