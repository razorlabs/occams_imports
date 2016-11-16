function ImputationList(data){
  'use strict';
  var self = this;

  self.operator = ko.observable('ALL');
  self.imputations = ko.observableArray();

  self.imputationsLength = ko.pureComputed(function(){
    return self.imputations().length;
  });

  self.hasImputations = ko.pureComputed(function(){
    return self.imputationsLength() > 0;
  });

  self.hasMultipleImputations = ko.pureComputed(function(){
    return self.imputationsLength() > 1;
  });

  self.addImputation = function(after){
    var index = after ? self.imputations.indexOf(after) : self.imputationsLength();
    self.imputations.splice(index + 1, 0, new Imputation());
  };

  self.removeImpuation = function(imputation){
    self.imputations.remove(imputation);
  };

  self.update = function(data){
    data = data || {};
    self.operator(data.operator);
    self.imputations((data.imputations || []).map(function(value){
      return new Imputation(value);
    }));
  };

  self.update(data);
};


function Imputation(data){
  'use strict';
  var self = this;

  // EQ/NE/LT/LTE
  self.operator = ko.observable();
  self.value = ko.observable();

  self.update = function(data){
    data = data || {};
    self.operator(data.operator);
    self.value(data.value);
  };

  self.update(data);
}
