$(document).ready(() => {
  // Submit editing user's balance
  $("#edit").click(() => {
    const para = {
      balance: $("#balance").val()
    }
    console.log(`/u/${window.location.href.split('/').pop()}`)
    $.post(
      `/u/${window.location.href.split('/').pop()}`, 
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
  $("#print").click(() => window.location.replace(`/print/u/${$('#clientId').val() || ''}`))
})