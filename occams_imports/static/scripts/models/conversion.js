function Conversion (data){
  'use strict';
  var self = this;

  self.operator = ko.observable();
  self.value = ko.observable();

  self.byVariable = ko.pureComputed(function(){
    var value = self.value();
    return value && value instanceof Variable;
  });

  self.byValue = ko.pureComputed(function(){
    var value = self.value();
    return value && !(value instanceof Variable);
  });

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
