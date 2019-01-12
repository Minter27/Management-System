$(document).ready(() => {
  $("#submit").click(() => {
    if ($("#username").value === '' || $("#password").value === '') {
      alert("You have to have a username!")
      $("form").submit((event) => {
        event.preventDefault();
        event.stopPropagation();
      })
    }
    else {
      $.ajax({
        method: "POST",
        url: "/login",
        data: {
          username: $("#username").value,
          password: $("#password").value
        }
      })
    }
  })
})