$(document).ready(() => {
  $("#add").click(() => {
    const para = {
      id: $("#itemId").val(),
      name: $("#itemName").val(),
    }
    console.log(para)
    $.post("/inventory", para, (data) => {
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