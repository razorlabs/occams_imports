function Conversion (data){
  'use strict';
  var self = this;

  self.operator = ko.observable();
  self.value = ko.observable();

  self.byVariable = ko.pureComputed(function(){
    return self.value() instanceof Variable;
  });

  self.byValue = ko.pureComputed(function(){
    return !self.byVariable();
  });

  self.changeType = function(data, event){
    self.value(event.target.value == 'VAR' ? new Variable() : null);
  };

  self.update = function(data){
    data = data || {};
    self.operator(data.operator);
    if (typeof data.value === 'object'){
      self.value(new Variable(data.value));
    } else {
      self.value(data.value);
    }
  };

  self.update(data);
}
