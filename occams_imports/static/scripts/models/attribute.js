function Attribute (data){
  'use strict';

  var self = this;

  self.name = ko.observable();
  self.title = ko.observable();
  self.type = ko.observable();

  self.hasChoices = ko.pureComputed(function(){
    return self.type() === 'choice';
  });

  self.update = function(data){
    data = data || {};
    self.name(data.name);
    self.title(data.title);
    self.type(data.type);
  };

  self.update(data);
}

