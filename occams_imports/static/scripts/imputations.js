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
  self.selectedOperator = ko.observable();
  self.value = ko.observable();
}

comparisonModel.prototype.toJSON = function() {
  // remove unnecessary operators attribute to clean up
  // ko.JSON results
  'use strict'

  var self = this;

  var copy = ko.toJS(self);
  delete copy.operators;

  return copy;
}

function logicalModel(){
  'use strict'

  var self = this;

  self.operators = ko.observableArray(['and', 'or']);
  self.comparisons = ko.observableArray([]);
  self.selectedOperator = ko.observable();

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

logicalModel.prototype.toJSON = function() {
  // remove unnecessary operators attribute to clean up
  // ko.JSON results
  'use strict'

  var self = this;

  var copy = ko.toJS(self);
  delete copy.operators;

  return copy;
}

function conversionModel(){
  'use strict'

  var self = this;

  self.mathOperators = ko.observableArray(['multiply', 'divide', 'add', 'subtract']);
  self.selectedOperator = ko.observable();
  self.selectedForm = ko.observable();
  self.selectedAttribute = ko.observable();
  self.newConversion = ko.observable(false);
  self.value = ko.observable();
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

  self.forms = ko.observableArray();
  self.selectedForm = ko.observable();
  self.selectedAttribute = ko.observable();

  self.conversions = ko.observableArray();

  self.drsc_forms = ko.observableArray();
  self.selectedDRSCForm = ko.observable();
  self.selectedDRSCAttribute = ko.observable();

  self.isSuccess = ko.observable(false);
  self.isDanger = ko.observable(false);
  self.msgType = ko.observable('Info - ');
  self.msg = ko.observable('Please select a form after loading.');
  self.isInfo = ko.observable(true);

  self.addLogicalOperator = function(){
    self.logicalOperators.push(new logicalModel());

  }

  self.addComparisonOperator = function(){
    'use strict'

    var self = this;

    self.comparisonOperators.push(new comparisonModel());
  }

  self.addConversion = function(){
    'use strict'

    var self = this;

    self.conversions.push(new conversionModel());
  }

  self.deleteComparisonOperator = function(){
    'use strict'

    var self = this;

    self.comparisonOperators.pop()
  }

  self.deleteConversion = function(){
    'use strict'

    var self = this;

    self.conversions.pop()
  }

  self.deleteLogicalOperator = function(){
    'use strict'

    var self = this;

    self.logicalOperators.pop()
  }

  self.saveImputation = function(){
    'use strict'

    var self = this;

    if (self.selectedDRSCForm() === undefined){
      self.isInfo(false);
      self.msgType('Error - ');
      self.msg('Please select a form to apply imputation.');
      self.isDanger(true);
    }

    else {
    var data = ko.toJSON({logical: self.logicalOperators(),
                          comparison: self.comparisonOperators(),
                          selected_comparison_condition: self.selectedComparisonCondition,
                          drsc_form: self.selectedDRSCForm().name,
                          drsc_publish_date: self.selectedDRSCForm().publish_date,
                          drsc_variable: self.selectedDRSCAttribute().variable,
                          conversions: self.conversions()})

    self.isInfo(false);
    self.isDanger(false);
    self.msgType('Success - ');
    self.msg('Imputation inserted into the database.');
    self.isSuccess(true);

    console.log(data);
    }
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
          self.forms.push(form);
        }
        else{
          self.drsc_forms.push(form);
        }
      });
    },
    complete: function(){
      self.addConversion();
      self.isLoading(false);
  }
  });

}