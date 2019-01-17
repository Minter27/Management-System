$(document).ready(() => {
  $('#next').click(() => {
    const para = {
      transactionId: $('#transactionId').val(),
      descreption: $('#descreption').val(),
      amount: $('#amount').val(),
    }
    if ( para.amount <= 0 || para.descreption.length < 3 ) {
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