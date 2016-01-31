var $container = $('#bundle_covers');

$container.masonry({
  itemSelector : '.item-selector',
});

$(function() {
  $("img.lazy").lazyload({
    threshold: 200,
    effect: 'fadeIn'
  });
});


function post_to_url(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
         }
    }

    document.body.appendChild(form);
    form.submit();
}

// PK 
$(function() {
  if (typeof pic_ids === 'undefined') {
    return
  }
  $("a img").click(function() {
    var win = $(this).attr('data-id');
    var lose = pic_ids[0] == win ? pic_ids[1] : pic_ids[0];
    post_to_url('http://' + MNP.hostname + '/pk', {win: win, lose: lose}, 'post');
  });
});
