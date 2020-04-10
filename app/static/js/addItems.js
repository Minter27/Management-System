const round = (number) => {
  return (Math.floor(number * 1000) / 1000)
}

$(document).ready(() => {
  let lengths = {}

  $.getJSON('/getTypes', null, data => {
    for (let type of data){
      $("#itemName").append(
        `<option value=${type.id}>${type.name}</option>`
      )
    }
    lengths.types = data.length
  })

  $("#itemId").change(function() {
    $('#itemName option:selected').removeAttr('selected')
    if (this.value > 0 && this.value <= lengths.types) {
      $(`#itemName option[value=${this.value}]`).attr('selected', 'selected')
    } else {
      $('#stdoption').attr('selected', 'selected')
      this.value = ''
      alert('لا يوجد صنف بهذا الرقم')
    }
  })

  $('#itemName').on('change', function() {
    $("#itemId").val(this.value)
  })

  $('#itemStock').on('change', () => {
    $('#total').val(round($('#itemPrice').val() * $('#itemStock').val()))
  })
  $('#itemPrice').on('change', () => {
    $('#total').val(round($('#itemStock').val() * $('#itemPrice').val()))
  })

  $('#next').click(() => {
    const para = {
      transactionId: $('#transactionId').val(),
      itemId: $('#itemId').val(),
      itemPrice: $('#itemPrice').val(),
      itemStock: $('#itemStock').val(),
      total: $('#total').val(),
    }
    console.log(para)
    if ( para.itemStock === 0 || para.itemPrice === 0){
      alert("تأكد من تعبئة النموذج صحيحاَ")
    }
    else {
      $.post('/addItems', para, (data) => {
        if (data[0] === "/")
          window.location.replace(data)
        else
          alert(data)
      })
    }
  })

  $("#clear").click(() => {
    const transactionId = $('#transactionId').val()
    $('input').val('')
    $('option').removeAttr('selected')
    $('#stdoption').attr('selected', 'selected')
    $('#transactionId').val(transactionId)
  })
})