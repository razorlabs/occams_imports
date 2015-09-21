function formModel(name, publish_date, variables){
  'use strict'

  var self = this;

  self.name = name;
  self.publish_date = publish_date;
  self.variables = ko.observableArray([])

  var variableLength = variables.length;

  for (var i = 0; i < variableLength; i++){
    self.variables.push(variables[i])
  }
}

function formViewModel(){
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
        var form = new formModel(this.name, this.publish_date, this.variables)
        self.forms.push(form)
      });
  }
  });

  self.forms = ko.observableArray();
  selectedForm = ko.observable()
}