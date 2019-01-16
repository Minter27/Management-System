const round = (number) => {
  return (Math.floor(number * 1000) / 1000)
}

$(document).ready(() => {
  const itemsArr = ["حديد مشكل", "حديد 10", "حديد 8", "اسمنت", "اسمنت ابيض اردني", "اسمنت ابيض اجنبي",
  "شيد", "سلك ناعم", "سلك مجدول", "مسامير عادي", "مسامير باطون", "كانات", "اسافين", "ستوك اردتي",
  "ستوك اجنبي"]
  for (let i in itemsArr){
    $("#itemName").append(
      `<option value=${parseInt(i, 10) + 1}>${itemsArr[i]}</option>`
    )
  }

  $("#itemId").change(() => {
    $('#itemName option:selected').removeAttr('selected')
    $(`#itemName option[value=${$("#itemId").val()}]`).attr('selected', 'selected')
  })

  $('#itemName').on('change', function (e) {
    const optionSelected = $("option:selected", this)
    const valueSelected = this.value
    $("#itemId").val(valueSelected)
  })

  $('#itemStock').on('change', () => {
    $('#total').val(round($('#itemPrice').val() * $('#itemStock').val()))
  })
  $('#itemPrice').on('change', () => {
    $('#total').val(round($('#itemStock').val() * $('#itemPrice').val()))
  })

  $('#next').click(() => {
    const para = {
      transactionId: $('#transactionId').val(),
      itemId: $('#itemId').val(),
      itemPrice: $('#itemPrice').val(),
      itemStock: $('#itemStock').val(),
      total: $('#total').val(),
    }
    console.log(para)
    if ( para.itemStock === 0 || para.itemPrice === 0){
      alert("تأكد من تعبئة النموذج صحيحاَ")
    }
    else {
      $.post('/addItems', para, (data) => {
        if (data[0] === "/")
          window.location.replace(data)
        else
          alert(data)
      })
    }
  })

  $("#clear").click(() => {
    const transactionId = $('#transactionId').val()
    $('input').val('')
    $('option').removeAttr('selected')
    $('#stdoption').attr('selected', 'selected')
    $('#transactionId').val(transactionId)
  })
})