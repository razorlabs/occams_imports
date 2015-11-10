function Group(data){
  'use strict';
  var self = this;

  self.title = ko.observable();
  self.conversions = ko.observableArray();
  self.logic = ko.observable();

  self.conversionsLength = ko.pureComputed(function(){
    return self.conversions().length();
  });

  self.update = function(data){
    data = data || {};
    self.conversions((data.conversions || []).map(function(value){
      return new Conversion(value);
    }));
    self.logic(new ImputationList(data.logic));
  };

  self.update(data);
}
