function Bucket(data){
  'use strict';

  var self = this;

  self.title = ko.observable();

  self.conversions = ko.observableArray();

  // Root imputation list
  self.imputation = ko.observable();

  self.conversionsLength = ko.pureComputed(function(){
    return self.conversions().length();
  });

  self.update = function(data){
    data = data || {};
    self.conversions((data.conversions || []).map(function(value){
      return new Conversion(value);
    }));
    self.imputation(new ImputationList(data.imputation));
  };

  self.update(data);
}
