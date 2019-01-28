$(document).ready(() => {
  $("#print").click(() => window.location.replace(`/print/u/${$('#clientId').val() || ''}`))
})