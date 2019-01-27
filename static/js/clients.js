$(document).ready(() => {
  $("#add").click(() => {
    const para = {
      id: $("#clientId").val(),
      name: $("#clientName").val(),
      phone: $("#clientPhone").val(),
      balance: $("#clientBalance").val()
    }
    console.log(para)
    $.post("/clients", para, (data) => {
      if (data[0] === "/")
        window.location.replace(data)
      else
        alert(data)
    })
  })

  $("#print").click(function() {
    window.location.replace(`/print/${$(this).val()}/~`)
  })
})