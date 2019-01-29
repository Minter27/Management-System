$(document).ready(() => {
  $(".type").click(function() {
    $(".type").removeClass('btn-primary').addClass('btn-secondary') 
    $(this).removeClass('btn-secondary').addClass('btn-primary')
    const para = {
      typeId: $(this).val(),
    }
    $.getJSON("/getTransactionsByType", para, (data) => {
      let total = 0
      $("tbody").empty()
      for (let transaction of data) { 
        $("tbody").append(
        `<tr>
          <th scope="row">${ transaction.id }</th>
          <td>${ transaction.clientId }</td>
          <td>${ transaction.amount }</td>
          <td>${ transaction.descreption }</td>
          <td>${ transaction.type }</td>
          <td>${ transaction.date }</td>
        </tr>`
        )
        total += transaction.amount
      }
      $("p#total").text("المجموع: " + total.toFixed(1))
    })
  })

  $('#print').click(() => {
    window.location.replace(`/print/u/1?typeId=${$('.btn-primary').val() || ''}`)
  })
})