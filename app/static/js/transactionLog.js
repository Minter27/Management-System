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
  let lengths = {}

  $('#search').click(() => {
    const date = {
      start: $('#dateStart').val(),
      end: $('#dateEnd').val()
    }
    $.getJSON('/transactionLog', date , (data) => {
      console.log(data)
      if (!data.error) {
        $('tbody').empty()
        for (let transaction of data.transactions) {
          $('tbody').append(
            `<tr>
              <th scope="row">${transaction.transactionId}</th>
              <td>${transaction.clientId}</td>
              <td>${transaction.clientName}</td>
              <td>${transaction.itemName}</td>
              <td>${transaction.weight}</td>
              <td>${transaction.description}</td>
              <td>${transaction.price}</td>
              <td>${transaction.total}</td>
              <td>${transaction.paid}</td>
              <td>${transaction.type}</td>
              <td>${transaction.date}</td>
              <td>
                <button 
                  type="button" 
                  class="btn btn-outline-dark" 
                  id="edit" 
                  value="${ transaction.transactionId }"
                  data-toggle="modal" 
                  data-target="#modal"
                >
                  تعديل
                </button>
              </td>
            </tr>`
          )
        }
      } else {
        alert(data.error)
      }
    })
  })

  $("#print").click(function() {
    window.location.replace(`/print/${$(this).val()}/~?dateStart=${$('#dateStart').val()}&dateEnd=${$('#dateEnd').val()}`)
  })

  $('body').on('DOMSubtreeModified', 'tbody', function() {
    console.log(this.value)
    $("button#edit").each(function() {
      $(this).click(function() {
        $("#transactionId").val(this.value)
        readyFormWithData()
      })
    })
  })

  $("button#edit").each(function() {
    $(this).click(function() {
      $("#transactionId").val(this.value)
      readyFormWithData()
    })
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

  $("#transactionId").change(readyFormWithData)

  $("#transactionId").focusout(function() {
    $("#save").removeAttr('disabled')
  })
  $("#transactionId").focusin(function() {
    $("#save").attr('disabled', 'disabled')
  })

  $.getJSON('/getClients', null, clients => {
    for (let client of clients){
      //if (client.id === 1) continue
      //else 
      if (client.id < 0) {
        alert('حدث خطأ. الرجاء اعادة التشغيل')
        break
      }
      $("#clientName").append(
        `<option value=${client.id}>${client.name}</option>`
      )
    }
    lengths.clients = clients.length
  })

  $.getJSON('/getTypes', null, data => {
    for (let type of data){
      $("#item").append(
        `<option value=${type.id}>${type.name}</option>`
      )
    }
  })

  $("#clientId").change(function() {
    $('#clientName option:selected').removeAttr('selected')
    if (this.value > 1 && this.value <= lengths.clients) {
      $(`#clientName option[value=${this.value}]`).attr('selected', 'selected')
    } else {
      $('#stdoption2').attr('selected', 'selected')
      this.value = ''
      alert('لا يوجد عميل بهذا الرقم')
    }
  })

  $('#clientName').on('change', function () {
    $("#clientId").val(this.value)
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