$(document).ready(function() {
  $.ajaxSetup({ cache: false,
                async: true });

  $('button[name=stop_pic]').click(function() {
    $.ajax({
      url: '/stop_pic'
    });
  });

  $('button[name=start_pic]').click(function() {
    $.ajax({
      url: '/start_pic'
    });
  });
});