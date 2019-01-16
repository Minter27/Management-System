$(document).ready(() => {
  $('#search').click(() => {
    const date = {
      start: $('#dateStart').val(),
      end: $('#dateEnd').val()
    }
    console.log(date)
    /* date.start = date.start.split('-').reverse().join('-')
    date.end = date.end.split('-').reverse().join('-') */
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
            <td>${transaction.date}</td>
          </tr>`
        )
      }
    })
  })
})