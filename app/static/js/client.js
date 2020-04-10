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
          $('#clientId').val(data.clientId)
          selectOnValue('clientName', data.clientId)
          $('#description').val(data.description)
          $('#total').val(data.total)
          $('#paid').val(data.paid)
          $('#transactionDetails').html("")
          let first = true
          for(let item of data.items) {
            if (first) {
              first = false
              let headrDiv = '<div class="form-row">'
              headrDiv += `<div class="form-group col-md-3">
                <label for="item">الصنف</label></div>`
              headrDiv += `<div class="form-group col-md-3">
                <label for="weight">الوزن/العدد</label></div>`
              headrDiv += `<div class="form-group col-md-3">
                <label for="price">السعر</label></div>`
              headrDiv += `<div class="form-group col-md-3">
                <label for="price">المجموع</label></div>`
              headrDiv += '</div>'
              $('#transactionDetails').append(headrDiv);
            }
            let mainDiv = '<div class="form-row">'

            mainDiv += `<div class="form-group col-md-3">
              <select class="form-control" name="item" id="item_${item.detailId}">
                <option selected="selected" value="${item.itemId}" disabled="disabled">${item.itemName}</option>
              </select></div>`
            mainDiv += `<div class="form-group col-md-3">
                <input class="form-control" name="weight" id="weight_${item.detailId}" placeholder="الوزن/العدد" 
                type="number" step="0.005" value="${item.weight}"/>
              </div>`
            mainDiv += `<div class="form-group col-md-3">
                <input class="form-control" name="price" id="price_${item.detailId}" placeholder="بالدينار" 
                type="number" step="0.005" value="${item.price}"/>
              </div>`
            mainDiv += `<div class="form-group col-md-3">
                <input class="form-control" name="itemTotal" id="itemTotal_${item.detailId}" placeholder="بالدينار" 
                type="number" step="0.005" value="${item.price * item.weight}"/>
              </div>`
            mainDiv += '</div>'
            $('#transactionDetails').append(mainDiv);
          }
          
          $('[name="weight"]').on('change', updateTotal());
          
          $('[name="price"]').on('change', updateTotal());
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

  $("#save").click(() => {
    let itemCounts = $('[name="itemTotal"]')
    let items = []
    for(let itemDetail of itemCounts) {
      let detailId = itemDetail.id.split("_")[1]
      items.push({
        detailId: detailId,
        itemId: $('#item_' + detailId + ' option:selected').val(),
        weight: $('#weight_' + detailId).val(),
        price: $('#price_' + detailId).val(),
      });
    }

    const para = {
      transactionId: $('#transactionId').val(),
      typeId: $('#transactionType option:selected').val(),
      typeName: $("#transactionType option:selected").text(),
      clientId: $('#clientId').val(),
      description: $('#description').val(),
      total: $('#total').val() || "0",
      paid: $('#paid').val() || "0",
      items: JSON.stringify(items),
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


function updateTotal() {
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