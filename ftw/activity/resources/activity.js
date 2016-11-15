(function($) {
  $(document).on('ready reload', function() {
    var events = $('.activity .events');
    if(events.length === 0) {
      return;
    }

    if(events.find('.more-button').length > 0) {
      return;
    }

    if (events.find('.event').length === 0) {
      return;
    }

    var fetch_url = events.data('fetch-url');
    var more = $('<a />').
        attr('href', '#').
        addClass('more-button').
        text(events.data('more-label')).
        insertAfter(events);

    more.click(function(event) {
      event.preventDefault();

      var last_activity = events.find('.event:last').data('activity-id');
      var url = fetch_url + "?last_activity=".concat(last_activity);

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
    if($('.activity .event:last').data('is-last-activity') == 'True') {
      $('.activity .more-button').hide();
    }
  });
})(jQuery);
