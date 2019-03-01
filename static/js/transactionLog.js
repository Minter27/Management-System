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
  $('#search').click(() => {
    const date = {
      start: $('#dateStart').val(),
      end: $('#dateEnd').val()
    }
    console.log(date)
    $.getJSON('/transactionLog', date , (data) => {
      console.log(data)
      $('tbody').empty()
      for (let transaction of data.transactions) {
        $('tbody').append(
          `<tr>
            <th scope="row">${transaction.transactionId}</th>
            <td>${transaction.clientId}</td>
            <td>${transaction.itemName}</td>
            <td>${transaction.weight}</td>
            <td>${transaction.descreption}</td>
            <td>${transaction.price}</td>
            <td>${transaction.total}</td>
            <td>${transaction.paid}</td>
            <td>${transaction.type}</td>
            <td>${transaction.date}</td>
          </tr>`
        )
      }
    })
  })

  $("#print").click(function() {
    window.location.replace(`/print/${$(this).val()}/~?dateStart=${$('#dateStart').val()}&dateEnd=${$('#dateEnd').val()}`)
  })

  const readyFormWithData = () => {
    $("#transactionType").attr('disabled', 'disabled')
    $.getJSON("/getTransactionById", { transactionId: $("#transactionId").val() }, (data) => {
      if (data.typeId) {
        $('select, input:not(#total)').not("#transactionType").removeAttr('disabled')
        if (data.typeId === "R" || data.typeId === "E") {
          $("#weight, #item, #price").attr('disabled', 'disabled')
        }
        else if (data.typeId == "B") { 
          $("#paid, #clientId, #clientName").attr('disabled', 'disabled')
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
  }

  $("button#edit").each(function() {
    console.log(this.value)
    $(this).click(() => {
      //TODO SEND TRANSACTIONID TO GET INFO TO RENDER IN THE MODAL BEING TRIGGERED
      console.log("HERE", this.value)
      $("#transactionId").val(this.value)
      readyFormWithData()
    })
  })

  $("#transactionId").change(readyFormWithData)

  $("#transactionId").focusout(function() {
    $("#save").removeAttr('disabled')
  })
  $("#transactionId").focusin(function() {
    $("#save").attr('disabled', 'disabled')
  })

  $("#clientId").change(() => {
    selectOnValue('clientName', $("#clientId").val())
  })

  const itemsArr = ["حديد مشكل", "حديد 10", "حديد 8", "اسمنت", "اسمنت ابيض اردني", "اسمنت ابيض اجنبي",
  "شيد", "سلك ناعم", "سلك مجدول", "مسامير عادي", "مسامير باطون", "اسافين", "ستوك اردتي",
  "ستوك اجنبي", "مثلث صغير", "مربع", "مثلث", "60x15", "50x15", "50x18", "48x15", "45x15", "40x18", "40x15", "30x18", 
  "30x15"]
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
  
  $('#clientName').on('change', function () {
    $("#clientId").val(this.value)
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
      next: "transactionLog",
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
    $('input').val('')
    $('select, input:not(#total)').removeAttr('disabled')
    $('option').removeAttr('selected')
    $('#stdoption1').attr('selected', 'selected')
    $('#stdoption2').attr('selected', 'selected')
    $('#stdoption3').attr('selected', 'selected')
  })
})