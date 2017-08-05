$(document).ready(function() {

    // AJAX GET
    $('.get-more').click(function(){

        $.ajax({
            type: "GET",
            url: "/ajax/more/",
            success: function(data) {
            $('.contactList').empty();
            if (data.length > 0){
            for(i = 0; i < data.length; i++){
              $('.contactList').append('<li class="list-group-item"><a type="button" class="getDetails"  value="'+data[i]["name"]+'"><strong>'+data[i]["name"]+'</strong></a></li>');
            }
          }
            else {
                $('.contactList').append('<li class="list-group-item"><a type="button" class="getDetails"  value=""><strong>No Contacts Found</strong></a></li>');
            }
        }
        });

    });

    $("#searchBox").change(function(){
      searchText= $("#searchBox").val()
      urlStr= "/ajax/search/?q=" + searchText
      $.ajax({
          type: "GET",
          url: urlStr,
          success: function(data) {
          $('.contactList').empty();
          if (data.length > 0){
          for(i = 0; i < data.length; i++){
              $('.contactList').append('<li class="list-group-item"><a type="button" class="getDetails"  value="'+data[i]["name"]+'"><strong>'+data[i]["name"]+'</strong></a></li>');
          }
        }
          else {
              $('.contactList').append('<li class="list-group-item"><a type="button" class="getDetails"  value=""><strong>No contacts found for - ' + searchText +'</strong></a></li>');
          }
      }
      });
    });

    $(document).on('click', '.getDetails', function(){
      nameVal=$(this).attr('value');
      urlStr= "/ajax/details/?i=" + nameVal
      $.ajax({
          type: "GET",
          url: urlStr,
          success: function(data) {
          $('.DetailsPhoneNumber').text(data[0]["phone"])
          $('.DetailsEmailID').text(data[0]["email"])
          $('.DetailsAddress').text(data[0]["adress"])
          $('.ContactNameHeader').text(data[0]["name"])
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
                alert(data.message);
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
