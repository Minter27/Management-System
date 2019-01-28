const round = (number) => {
  return (Math.floor(number * 1000) / 1000)
}

$(document).ready(() => {
  $("#clientId").change(() => {
    $('#clientName option:selected').removeAttr('selected')
    $(`#clientName option[value=${$("#clientId").val()}]`).attr('selected', 'selected')
  })

  const itemsArr = ["حديد مشكل", "حديد 10", "حديد 8", "اسمنت", "اسمنت ابيض اردني", "اسمنت ابيض اجنبي",
  "شيد", "سلك ناعم", "سلك مجدول", "مسامير عادي", "مسامير باطون", "كانات", "اسافين", "ستوك اردتي",
  "ستوك اجنبي"]
  for (let i in itemsArr){
    $("#item").append(
      `<option value=${parseInt(i, 10) + 1}>${itemsArr[i]}</option>`
    )
  }

  $.getJSON('/getClients', null, (data) => {
    for (let client in data.clientArr){
      $("#clientName").append(
        `<option value=${parseInt(client, 10) + 1}>${data.clientArr[client]}</option>`
      )
    }
  })
  
  $('#clientName').on('change', function (e) {
    const optionSelected = $("option:selected", this)
    const valueSelected = this.value
    $("#clientId").val(valueSelected)
  })

  $('#weight').on('change', () => {
    $('#total').val(round($('#price').val() * $('#weight').val()))
  })
  $('#price').on('change', () => {
    $('#total').val(round($('#weight').val() * $('#price').val()))
  })

  $("#next").click(() => {
    const para = {
      transactionId: $('#transactionId').val(),
      clientId: $('#clientId').val(),
      itemId: $('#item option:selected').val(),
      weight: $('#weight').val(),
      descreption: $('#descreption').val(),
      price: $('#price').val(),
      total: $('#total').val(),
      paid: $('#paid').val(),
    }
    console.log(para)
   $.post('/transaction', para, (data) => {
      if (data[0] === "/")
        window.location.replace(data)
      else
        alert(data)
   })
})

  $("#clear").click(() => {
    const transactionId = $('#transactionId').val()
    $('input').val('')
    $('option').removeAttr('selected')
    $('#stdoption1').attr('selected', 'selected')
    $('#stdoption2').attr('selected', 'selected')
    $('#transactionId').val(transactionId)
  })
})