$(document).ready(() => {
  $("#clientId").change(() => {
    $('#clientName option:selected').removeAttr('selected')
    $(`#clientName option[value=${$("#clientId").val()}]`).attr('selected', 'selected')
  })

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

  $('#next').click(() => {
    const para = {
      transactionId: $('#transactionId').val(),
      clientId: $('#clientId').val(),
      amount: $('#amount').val(),
    }
    if ( para.amount <= 0 || para.clientId <= 0 ) {
      alert("الرجاء التأكد من تعبئة النموذج صحيحاَ")
    }
    else {
      $.post('/repayDebt', para, (data) => {
        if (data[0] === "/")
          window.location.replace(data)
        else
          alert(data)
      })
    }
  })
})