$(document).ready(() => {
  $('#search').click(() => {
    const date = {
      start: $('#dateStart').val(),
      end: $('#dateEnd').val()
    }
    console.log(date)
  })
})