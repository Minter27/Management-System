const round = (number) => {
  return (Math.floor(number * 1000) / 1000)
}

$(document).ready(() => {
  let lengths = {}

  $.getJSON('/getTypes', null, types => {
    for (let type of types){
      $('[name="item"]').append(
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

  $('[name="weight"]').on('change', updateTotalByPrice());
  
  $('[name="price"]').on('change', updateTotalByPrice());

  $("#next").click(() => {
    let itemCounts = $('[name="itemTotal"]').length
    let items = []
    for(var i=1; i <= itemCounts; i++ ) {
      if(!$('#price_' + i).val()) {
        continue;
      }
      items.push({
        itemId: $('#item_' + i + ' option:selected').val(),
        weight: $('#weight_' + i).val(),
        price: $('#price_' + i).val(),
      });
    }
    const para = {
      transactionId: $('#transactionId').val(),
      clientId: $('#clientId').val(),
      description: $('#description').val(),
      total: $('#total').val(),
      paid: $('#paid').val(),
      items: JSON.stringify(items)
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

function updateTotalByPrice() {
  return (event) => {
    let index = event.target.id.split("_")[1]
    $('#itemTotal_' + index).val(round($('#price_' + index).val() * $('#weight_' + index).val()))
    let itemTotals = $('[name="itemTotal"]')
    let total = 0
    for (let itemTotal of itemTotals) {
      if (itemTotal.value)
        total += parseInt(itemTotal.value)
    }
    $('#total').val(total)
  }
}
