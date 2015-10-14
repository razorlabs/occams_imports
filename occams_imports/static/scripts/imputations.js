function comparisonModel(){
  'use strict';

  var self = this;

  self.operators = ko.observableArray(['==', '!=', '>', '<', '>=', '<=']);
  self.value = ko.observable();
}

function logicalModel(){
  'use strict'

  var self = this;

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
    'use strict'

    var self = this;

    self.comparisonOperators.push(new comparisonModel());
  }

  self.deleteComparisonOperator = function(){
    'use strict'

    var self = this;

    self.comparisonOperators.pop()
  }

  self.deleteLogicalOperator = function(){
    'use strict'

    var self = this;

    self.logicalOperators.pop()
  }

  self.saveImputation = function(){
    'use strict'

    var self = this;

    var data = ko.toJSON({logical: self.logicalOperators(),
                          comparison: self.comparisonOperators()})
    console.log(data);
  }

}