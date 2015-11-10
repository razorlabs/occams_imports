function ImputationList(data){
  'use strict';
  var self = this;

  self.operator = ko.observable('ALL');
  self.imputations = ko.observableArray();

  self.imputationsLength = ko.pureComputed(function(){
    return self.imputations().length;
  });

  self.hasMultiple = ko.pureComputed(function(){
    return self.imputationsLength() > 1;
  });

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
