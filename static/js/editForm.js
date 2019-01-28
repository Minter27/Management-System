const round = (number) => {
  return (Math.floor(number * 1000) / 1000)
}

const selectOnValue = (elementId, selectValue) => {
  try {
    $(`#${elementId} option:selected`).removeAttr('selected')
    $(`#${elementId} option[value=${selectValue}]`).attr('selected', 'selected')
  } catch(err) {
    console.error(err)
    return
  }
}

$(document).ready(() => {
  $("#transactionId").change(() => {
    $("#transactionType").attr('disabled', 'disabled')
    $.getJSON("/getTransactionById", { transactionId: $("#transactionId").val() }, (data) => {
      if (data.typeId) {
        $('select, input:not(#total)').not("#transactionType").removeAttr('disabled')
        if (data.typeId === "R" || data.typeId === "E") {
          $("#weight, #item, #price").attr('disabled', 'disabled')
        }
        else if (data.typeId == "B") { 
          $("#paid").attr('disabled', 'disabled')
        }
        try {
          selectOnValue('transactionType', `"${data.typeId}"`)
          $('#clientId').val(data.clientId)
          selectOnValue('clientName', data.clientId)
          selectOnValue('item', data.itemId || '0')
          $('#weight').val(data.weight)
          $('#descreption').val(data.descreption)
          $('#price').val(data.price)
          $('#total').val(data.total)
          $('#paid').val(data.paid)
        } catch(err) {
          console.error(err)
        }
      } 
      else 
        alert(data.status)
    })
  })

  $("#clientId").change(() => {
    selectOnValue('clientName', $("#clientId").val())
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
    const valueSelected = this.value
    $("#clientId").val(valueSelected)
  })

  $('#weight').on('change', () => {
    $('#total').val(round($('#price').val() * $('#weight').val()))
    $("#paid").val($("#total").val())
  })
  $('#price').on('change', () => {
    $('#total').val(round($('#weight').val() * $('#price').val()))
    $("#paid").val($("#total").val())
  })

  $("#save").click(() => {
    const para = {
      transactionId: $('#transactionId').val(),
      typeId: $('#transactionType option:selected').val(),
      typeName: $("#transactionType option:selected").text(),
      clientId: $('#clientId').val(),
      itemId: $('#item option:selected').val(),
      weight: $('#weight').val() || "0",
      descreption: $('#descreption').val(),
      price: $('#price').val() || "0",
      total: $('#total').val() || "0",
      paid: $('#paid').val() || "0",
    }
    console.log(para)
   $.post('/editTransactionForm', para, (data) => {
      if (data[0] === "/")
        window.location.replace(data)
      else
        alert(data)
   })
})

  $("#clear").click(() => {
    const transactionId = $('#transactionId').val()
    $('input').val('')
    $('select, input:not(#total)').removeAttr('disabled')
    $('option').removeAttr('selected')
    $('#stdoption1').attr('selected', 'selected')
    $('#stdoption2').attr('selected', 'selected')
    $('#stdoption3').attr('selected', 'selected')
    $('#transactionId').val(transactionId)
  })
})