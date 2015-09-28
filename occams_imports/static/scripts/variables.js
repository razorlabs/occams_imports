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

function mapVariable(){
  'use strict'

  var self = this;

  $.ajax({
    url: '/imports/mappings/direct/map',
    method: 'POST',
    headers: {'X-CSRF-Token': $.cookie('csrf_token')},
    beforeSend: function(){
    },
    success: function(data, textStatus, jqXHR){
      var json = $.parseJSON(data);

      self.isInfo(json['isInfo']);
      self.isSuccess(json['isSuccess']);
      self.msgType(json['msg_type']);
      self.msg(json['msg']);

    },
    complete: function(){
    }
  });
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
  self.isLoading = ko.observable(true);

  self.isDanger = ko.observable(false);
  self.isSuccess = ko.observable(false);
  self.msgType = ko.observable('Info - ');
  self.msg = ko.observable('Please select a form after loading.');
  self.isInfo = ko.observable(true);

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
    },
    complete: function(){
      self.isLoading(false);
  }
  });
}