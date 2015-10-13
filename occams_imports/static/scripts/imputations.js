function logicalModel(){
  'use strict';

  self.operators = ko.observableArray(['==', '!=', '>', '<', '>=', '<=']);
  self.value = ko.observable();
}

function imputationViewModel(){
  'use strict';

  var self = this;

  self.operators = ko.observableArray(['any', 'all']);
  self.selectedOperator = ko.observable();
  self.logicalOperators = ko.observableArray([]);

  self.addConditionalOperator = function(){

  }

  self.addLogicalOperator = function(){
    self.logicalOperators.push(new logicalModel());
  }

}