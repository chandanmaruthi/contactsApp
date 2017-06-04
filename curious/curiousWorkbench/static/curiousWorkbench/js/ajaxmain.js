$(document).ready(function() {

    // AJAX GET
    $('.get-more').click(function(){

        $.ajax({
            type: "GET",
            url: "/ajax/more/",
            success: function(data) {
            for(i = 0; i < data.length; i++){
                $('ul').append('<li>'+data[i]+'</li>');
            }
        }
        });

    });


    // AJAX POST
    $('.add-todo').click(function(){
      console.log('am i called');

        $.ajax({
            type: "POST",
            url: "/ajax/add/",
            dataType: "json",
            data: { "item": $(".todo-item").val() },
            success: function(data) {
                //alert(data.message);
            }
        });

    });



    // AJAX GET
    $(document).on("click", ".trashIcon",function() {
      console.log('am i called, trash icon');
      //alert(event.target.id);

      $.ajax({
          type: "POST",
          url: "/curiousWorkbench/delconv/",
          dataType: "json",
          data: { "id": event.target.id },
          success: function(data) {
              //alert('here');
              //$('.add-todo').click(function()).apply($('.add-todo'));
              $( '.get-conv' ).trigger( 'click');
          }
      });

    });



    // AJAX GET
    $('.get-conv').click(function(){
      console.log('am i called, get conv');
      //alert( $('.get-conv').val());
      var moduleID = $('.get-conv').val();
      //alert (moduleID);
        $.ajax({
            type: "GET",
            url: "/curiousWorkbench/getconv/" + moduleID  + "/",
            success: function(data) {
              $('.convList').empty();
            //alert ('ok here too');
            for(i = 0; i < data.length; i++){
                $('.convList').append('<div class="callout right">'+data[i]['text']+'</div><div class="calloutIconsBar"><input type="image" alt=" " src="/static/curiousWorkbench/images/invisible.png" class="editIcon" id="'+data[i]['id']+'"><div class="calloutIcons"  ><input type="image" alt=" " src="/static/curiousWorkbench/images/invisible.png" class="trashIcon" id="'+data[i]['id']+'"></div></div>');
            }
        }
        });

    });

    $(window).load(function(){
        // full load
        $( '.get-conv' ).trigger( 'click');
    });





    // AJAX POST
    $('.add-conv').click(function(){
      console.log('am i called, add conv');
      var moduleID = $('.get-conv').val()
      //alert(moduleID);
      urlStr  = "/curiousWorkbench/addconv/" + moduleID + "/";
      //alert(urlStr);
        $.ajax({
            type: "POST",
            url: urlStr,
            dataType: "json",
            data: { "item": $(".todo-item").val() },
            success: function(data) {
                //alert('end');
                $( '.get-conv' ).trigger( 'click');
                $(".todo-item").val('');

            }
        });

    });



    // CSRF code
    function getCookie(name) {
        var cookieValue = null;
        var i = 0;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (i; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


});
