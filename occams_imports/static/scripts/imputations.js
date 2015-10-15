function choiceModel(name, label){
  'use strict'

  var self = this;

  self.name = ko.observable(name);
  self.label = ko.observable(label);
  self.mapped = ko.observable('');
}

function attributeModel(variable, label, choices){
  'use strict'

  var self = this;

  self.variable = ko.observable(variable);
  self.label = ko.observable(label);
  self.choices = ko.observableArray([]);

  var choicesLength = choices.length;

  for (var i = 0; i < choicesLength; i++){
    self.choices.push(new choiceModel(choices[i].name, choices[i].label));
  }
}

function formModel(name, publish_date, attributes){
  'use strict'

  var self = this;

  self.name = ko.observable(name);
  self.publish_date = ko.observable(publish_date);
  self.attributes = ko.observableArray([]);

  var attributeLength = attributes.length;

  for (var i = 0; i < attributeLength; i++){
    self.attributes.push(
      new attributeModel(
        attributes[i].variable, attributes[i].label, attributes[i].choices));
  }
}

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
  self.comparisons = ko.observableArray([]);

  self.addComparisonOperator = function(){
    'use strict'

    var self = this;
    self.comparisons.push(new comparisonModel());
  }

  self.deleteComparisonOperator = function(){
    'use strict'

    var self = this;
    self.comparisons.pop()
  }
}

function imputationViewModel(){
  'use strict';

  var self = this;

  self.conditions = ko.observableArray(['any', 'all']);
  self.selectedComparisonCondition = ko.observable();
  self.comparisonOperators = ko.observableArray([]);
  self.logicalOperators = ko.observableArray([]);
  self.confidence = ko.observable(1);

  self.isReady = ko.observableArray(false);
  self.isLoading = ko.observable(true);

  self.drsc_forms = ko.observableArray();
  self.selectedDRSCForm = ko.observable();
  self.selectedDRSCAttribute = ko.observable();

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
                          comparison: self.comparisonOperators(),
                          selected_comparison_condition: self.selectedComparisonCondition})
    console.log(data);
  }

  $.ajax({
    url: '/imports/schemas',
    method: 'GET',
    headers: {'X-CSRF-Token': $.cookie('csrf_token')},
    beforeSend: function(){
      self.isReady(true);
    },
    success: function(data, textStatus, jqXHR){
      var json = $.parseJSON(data);

      $.each(json.forms, function(){
        var form = new formModel(this.name, this.publish_date, this.attributes);
        if (this.site != 'DRSC'){

        }
        else{
          self.drsc_forms.push(form);
        }
      });
    },
    complete: function(){
      self.isLoading(false);
  }
  });

}