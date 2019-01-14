$(document).ready(() => {
  $("#clientId").change(() => {
    $(`option[value=${$("#clientId").val()}`).attr('selected', 'selected')
  })

  const itemsArr = ["حديد مشكل", "حديد 10", "حديد 8", "اسمنت", "اسمنت ابيض اردني", "اسمنت ابيض اجنبي",
  "شيد", "سلك ناعم", "سلك مجدول", "مسامير عادي", "مسامير باطون", "كانات", "اسافين", "ستوك اردتي",
  "ستوك اجنبي"]
  for (let i in itemsArr){
    $("#itemName").append(
      `<option value=${i+1}>${itemsArr[i]}</option>`
    )
  }

  $.getJSON('/getClients', null, (data) => {
    for (let client in data.clientArr){
      $("#clientName").append(
        `<option value=${parseInt(client+1, 10)}>${data.clientArr[client]}</option>`
      )
    }
  })
  
  $('#clientName').on('change', function (e) {
    const optionSelected = $("option:selected", this)
    const valueSelected = this.value
    $("#clientId").val(valueSelected)
  })

  $("#next").click(() => {
    //TODO
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