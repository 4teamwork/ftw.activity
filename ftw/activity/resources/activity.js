(function($) {$(function() {

  var events = $('.activity .events');
  if(events.length === 0) {
    return;
  }

  var more = $('<a />').
      attr('href', '#').
      addClass('more-button').
      text(events.data('more-label')).
      insertAfter(events);

  more.click(function(event) {
    event.preventDefault();

    var last_uid = events.find('>.event:last').data('uid');
    var url = "activity/fetch?last_uid=".concat(last_uid);

    $.get(url, function(data) {
      if(data.trim().length) {
        $(data).appendTo(events);
      } else {
        more.remove();
      }
    });
  });


});})(jQuery);
