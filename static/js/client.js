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
  const clientId = $('#clientId').val()
  const transactionId = $("#transactionId")
  // Submit editing user's balance
  $("#editBalance").click(() => {
    const para = {
      balance: $("#balance").val()
    }
    console.log(`/u/${window.location.href.split('/').pop()}`)
    $.post(
      `/u/${clientId}`, 
      para,
      data => {
        if (data[0] === "/")
          window.location.replace(data)
        else
          alert(data)
      }
    )
  })

  // Make pdf for printing
  $("#print").click(() => window.location.replace(`/print/u/${clientId || ''}`))

  // Edit transaction per row
  $("button#editTransaction").each(function() {
    $(this).click(() => {
      transactionId.val(this.value)
      setTimeout(() => transactionId.attr('disabled', true), 10)
      readyFormWithData()
    })
  })

  const readyFormWithData = () => {
    $("#transactionType").attr('disabled', 'disabled')
    $.getJSON("/getTransactionById", { transactionId: transactionId.val() }, (data) => {
      if (data.typeId) {
        $('select, input:not(#total):not(#transactionType)').not(".constants").removeAttr('disabled')
        if (data.typeId === "R" || data.typeId === "E") {
          $("#weight, #item, #price").attr('disabled', 'disabled')
        }
        else if (data.typeId == "B") { 
          $("#paid").attr('disabled', 'disabled')
        }
        try {
          selectOnValue('transactionType', `"${data.typeId}"`)
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
  }

  $.getJSON('/getTypes', null, data => {
    for (let type of data){
      $("#item").append(
        `<option value=${type.id}>${type.name}</option>`
      )
    }
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
      transactionId: transactionId.val(),
      typeId: $('#transactionType option:selected').val(),
      typeName: $("#transactionType option:selected").text(),
      clientId: clientId,
      itemId: $('#item option:selected').val(),
      weight: $('#weight').val() || "0",
      descreption: $('#descreption').val(),
      price: $('#price').val() || "0",
      total: $('#total').val() || "0",
      paid: $('#paid').val() || "0",
      next: `u/${clientId}`,
    }
    console.log(para)
   $.post('/editTransactionForm', para, (data) => {
      if (data[0] === "/")
        window.location.replace(data)
      else
        alert(data)
   })
  })

  $("#modal").on('hidden.bs.modal', () => {
    $('input:not(.constants)').val('')
    $('select, input:not(#total)').not('.constants').removeAttr('disabled')
    $('option').removeAttr('selected')
    $('#stdoption1').attr('selected', 'selected')
    $('#stdoption2').attr('selected', 'selected')
  })
})