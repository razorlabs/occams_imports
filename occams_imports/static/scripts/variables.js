function attributeModel(variable, label){
  'use strict'

  var self = this;

  self.variable = ko.observable(variable);
  self.label = ko.observable(label);
}

function formModel(name, publish_date, attributes){
  'use strict'

  var self = this;

  self.name = ko.observable(name);
  self.publish_date = ko.observable(publish_date);
  self.attributes = ko.observableArray([])

  var attributeLength = attributes.length;

  for (var i = 0; i < attributeLength; i++){
    self.attributes.push(new attributeModel(attributes[i].variable, attributes[i].label))
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
        var form = new formModel(this.name, this.publish_date, this.attributes)
        self.forms.push(form)
      });
  }
  });

  self.forms = ko.observableArray();
  self.selectedForm = ko.observable()
}