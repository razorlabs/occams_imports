function Group(data){
  'use strict';
  var self = this;

  self.conversions = ko.observableArray();
  self.logic = ko.observable();

  self.conversionsLength = ko.pureComputed(function(){
    return self.conversions().length;
  });

  self.hasMultipleConversions = ko.pureComputed(function(){
    return self.conversionsLength() > 1;
  });

  self.addConversion = function(after){
    var conversion = new Conversion();
    if (!after){
      self.conversions.push(conversion);
    } else {
      var index = self.conversions.indexOf(after);
      self.conversions.splice(index + 1, 0, conversion);
    }
  };

  self.removeConversion = function(conversion){
    self.conversions.remove(conversion);
  };

  self.update = function(data){
    data = data || {};
    self.conversions((data.conversions || []).map(function(value){
      return new Conversion(value);
    }));
    self.logic(data.logic ? new ImputationList(data.logic) : null);
  };

  self.update(data);
}
