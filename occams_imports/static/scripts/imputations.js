function comparisonModel(){
  'use strict';

  self.operators = ko.observableArray(['==', '!=', '>', '<', '>=', '<=']);
  self.value = ko.observable();
}

function imputationViewModel(){
  'use strict';

  var self = this;

  self.operators = ko.observableArray(['any', 'all']);
  self.selectedOperator = ko.observable();
  self.comparisonOperators = ko.observableArray([]);

  self.addLogicalOperator = function(){

  }

  self.addComparisonOperator = function(){
    self.comparisonOperators.push(new comparisonModel());
  }

}