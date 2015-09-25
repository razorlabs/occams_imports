function choiceModel(name, label){
  'use strict'

  var self = this;

  self.name = ko.observable(name);
  self.label = ko.observable(label);

}

function attributeModel(variable, label, choices){
  'use strict'

  var self = this;

  self.variable = ko.observable(variable);
  self.label = ko.observable(label);
  self.choices = ko.observableArray([]);

  var choicesLength = choices.length;

  for (var i = 0; i < choicesLength; i++){
    self.choices.push(new choiceModel(choices[i].name, choices[i].label));
  }

}

function formModel(name, publish_date, attributes){
  'use strict'

  var self = this;

  self.name = ko.observable(name);
  self.publish_date = ko.observable(publish_date);
  self.attributes = ko.observableArray([]);

  var attributeLength = attributes.length;

  for (var i = 0; i < attributeLength; i++){
    self.attributes.push(
      new attributeModel(
        attributes[i].variable, attributes[i].label, attributes[i].choices));
  }
}

function formViewModel(){
  'use strict';

  var self = this;

  self.forms = ko.observableArray();
  self.drsc_forms = ko.observableArray();
  self.selectedForm = ko.observable();
  self.selectedDRSCForm = ko.observable();
  self.selectedAttribute = ko.observable();
  self.selectedDRSCAttribute = ko.observable();
  self.isReady = ko.observable(false);

  $.ajax({
    url: '/imports/schemas',
    method: 'GET',
    headers: {'X-CSRF-Token': $.cookie('csrf_token')},
    beforeSend: function(){
      self.isReady(true)
    },
    success: function(data, textStatus, jqXHR){
      var json = $.parseJSON(data);

      $.each(json.forms, function(){
        var form = new formModel(this.name, this.publish_date, this.attributes);
        if (this.site != 'DRSC'){
          self.forms.push(form);
        }
        else{
          self.drsc_forms.push(form);
        }
      });


  }
  });


}