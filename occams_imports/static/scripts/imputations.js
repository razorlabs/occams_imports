function imputationViewModel(){
  'use strict';

  var self = this;

  self.operators = ko.observableArray(['any', 'all']);
  self.selectedOperator = ko.observable();

}