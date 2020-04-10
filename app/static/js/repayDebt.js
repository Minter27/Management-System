$(document).ready(() => {
let lengths = {}

  $.getJSON('/getClients', null, clients => {
    for (let client of clients){
      if (client.id === 1) continue
      else if (client.id < 0) {
        alert('حدث خطأ. الرجاء اعادة التشغيل')
        break
      }
      $("#clientName").append(
        `<option value=${client.id}>${client.name}</option>`
      )
    }
    lengths.clients = clients.length
  })

  $("#clientId").change(function() {
    $('#clientName option:selected').removeAttr('selected')
    if (this.value > 1 && this.value <= lengths.clients) {
      $(`#clientName option[value=${this.value}]`).attr('selected', 'selected')
    } else {
      $('#stdoption').attr('selected', 'selected')
      this.value = ''
      alert('لا يوجد عميل بهذا الرقم')
    }
  })
  
  $('#clientName').on('change', function() {
    $("#clientId").val(this.value)
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