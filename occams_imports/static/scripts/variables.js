function Variable(){
  'use strict';

  var self = this;

  $.ajax({
    url: '/imports/schemas',
    method: 'GET',
   /* headers: {'X-CSRF-Token': $.cookie('csrf_token')},*/
    beforeSend: function(){
    },
    success: function(data, textStatus, jqXHR){
      var json = $.parseJSON(data)

      $.each(json.forms, function(){
        self.forms.push(this.name)
      });
  }
  });

  self.forms = ko.observableArray();
}