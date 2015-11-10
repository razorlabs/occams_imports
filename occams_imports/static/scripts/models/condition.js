var MAX_NESTING = 2;


ANY = {name: 'ANY', title: 'Any'};
ALL = {name: 'ALL', title: 'All'};

EQ = {name: 'EQ', title: 'is equal to'};
NE = {name: 'NE', title: 'is not equal to'};
LT = {name: 'LT', title: 'is is less than'};
LTE = {name: 'LTE', title: 'is less than or equal to'};
GT = {name: 'GT', title: 'is greater than'};
GTE = {name: 'GTE', title: 'is greater than or equal to'};

LOGICAL = [ANY, ALL];
COMPARISON = [EQ, NE, LT, LTE, GT, GTE];

function ImputationList(data){
  'use strict';
  var self = this;

  self.availableOperators = LOGICAL;

  self.operator = ko.observable(ALL);
  self.imputations = ko.observableArray();

  self.imputationsLength = ko.pureComputed(function(){
    return self.imputations().length;
  });

  self.hasMultiple = ko.pureComputed(function(){
    return self.imputationsLength() > 1;
  });

  self.update = function(data){
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

  self.availableOperators = COMPARISON;

  // EQ/NE/LT/LTE
  self.operator = ko.observable();
  self.value = ko.observable();

  self.selectedOperator = ko.observable();
  self.selectedValue = ko.observable();

  self.update = function(data){
    data = data || {};
    self.operator(data.operator);
    self.value(data.value);
  };

  self.update(data);
}
