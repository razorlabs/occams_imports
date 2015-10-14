function comparisonModel(){
  'use strict';

  self.operators = ko.observableArray(['==', '!=', '>', '<', '>=', '<=']);
  self.value = ko.observable();
}

function logicalModel(){
  self.operators = ko.observableArray(['and', 'or']);
}

function imputationViewModel(){
  'use strict';

  var self = this;

  self.operators = ko.observableArray(['any', 'all']);
  self.selectedOperator = ko.observable();
  self.comparisonOperators = ko.observableArray([]);
  self.logicalOperators = ko.observableArray([]);

  self.addLogicalOperator = function(){
    self.logicalOperators.push(new logicalModel());

  }

  self.addComparisonOperator = function(){
    self.comparisonOperators.push(new comparisonModel());
  }

  self.deleteComparisonOperator = function(){
    self.comparisonOperators.pop()
  }

}