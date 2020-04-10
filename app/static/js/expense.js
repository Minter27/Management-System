$(document).ready(() => {
  $('#next').click(() => {
    const para = {
      transactionId: $('#transactionId').val(),
      description: $('#description').val(),
      amount: $('#amount').val(),
    }
    if ( para.amount <= 0 || para.description.length < 3 ) {
      alert("الرجاء التأكد من تعبئة النموذج صحيحاَ")
    }
    else {
      $.post('/expense', para, (data) => {
        if (data[0] === "/")
          window.location.replace(data)
        else
          alert(data)
      })
    }
  })
})