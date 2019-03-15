const round = (number) => {
  return (Math.floor(number * 1000) / 1000)
}

$(document).ready(() => {
  let lengths = {}

  $.getJSON('/getTypes', null, types => {
    for (let type of types){
      $("#item").append(
        `<option value=${type.id}>${type.name}</option>`
      )
    }
  })

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
      $('#stdoption1').attr('selected', 'selected')
      this.value = ''
      alert('لا يوجد عميل بهذا الرقم')
    }
  })
  
  $('#clientName').on('change', function() {
    $("#clientId").val(this.value)
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