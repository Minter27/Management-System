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
})