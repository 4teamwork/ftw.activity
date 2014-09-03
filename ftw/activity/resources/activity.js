(function($) {
  $(document).on('ready reload', function() {
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

      var last_uid = events.find('.event:last').data('uid');
      var url = "activity/fetch?last_uid=".concat(last_uid);

      $.get(url, function(data) {
        if(data.trim().length) {
          var old_events = events.find('.event');
          $(data).appendTo(events);
          var new_events = events.find('.event').not(old_events);
          events.trigger('activity-fetched', [new_events]);
        } else {
          more.remove();
        }
      });
    });
  });

  $(document).on('ready reload activity-fetched', function() {
    if(typeof($.fn.colorbox) !== 'undefined') {
      $('.activity a.colorboxLink').colorbox({
        'photo': true,
        'current': '{current}/{total}',
        'maxWidth': '100%',
        'maxHeight': '100%'
      });
    }
  });
})(jQuery);
