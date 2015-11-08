function choiceImputationModel(name, label){
  'use strict'

  var self = this;

  self.name = ko.observable(name);
  self.label = ko.observable(label);
  self.mapToOptions = ko.pureComputed(function(){
    return self.name() + ' - ' + self.label();
  });

}

function attributeImputationModel(variable, label, choices, datatype){
  'use strict'

  var self = this;

  self.variable = ko.observable(variable);
  self.label = ko.observable(label);
  self.choices = ko.observableArray([]);
  self.datatype = ko.observable(datatype);

  var choicesLength = choices.length;

  for (var i = 0; i < choicesLength; i++){
    self.choices.push(new choiceImputationModel(choices[i].name, choices[i].label));
  }
}

function formImputationModel(name, publish_date, attributes){
  'use strict'

  var self = this;

  self.name = ko.observable(name);
  self.publish_date = ko.observable(publish_date);
  self.attributes = ko.observableArray([]);

  var attributeLength = attributes.length;

  for (var i = 0; i < attributeLength; i++){
    self.attributes.push(
      new attributeImputationModel(
        attributes[i].variable, attributes[i].label,
        attributes[i].choices, attributes[i].datatype));
  }
}

function conversionModel(){
  'use strict'

  var self = this;

  self.mathOperators = ko.observableArray(['multiply', 'divide', 'add', 'subtract']);
  self.operatorChoices = ko.observableArray(['By variable', 'By value'])
  self.selectedOperator = ko.observable();
  self.selectedOperatorChoice = ko.observable();
  self.selectedForm = ko.observable();
  self.selectedAttribute = ko.observable();
  self.value = ko.observable();

  self.select2AttributeParams = function(term, page){
    return {
      vocabulary: 'available_attributes',
      schema: self.selectedForm().name,
      term: term
    };
  };

  self.select2AttributeResults = function(data){
    return {
        results: data.attributes.map(function(value){
          return new attributeImputationModel(
            value.variable, value.label, value.choices, value.datatype)
        })
    };
  };

  self.select2SchemaParams = function(term, page){
    return {
      vocabulary: 'available_schemata',
      is_target: false,
      term: term
    };
  };

  self.select2SchemaResults = function(data){
    return {
        results: data.forms.map(function(value){
          return new formImputationModel(
            value.name, value.publish_date, value.attributes);
        })
    };
  };


}

conversionModel.prototype.toJSON = function(){
  'use strict'

  var self = this;

  var copy = ko.toJS(self);
  delete copy.mathOperators;
  delete copy.selectedAttribute.label;
  delete copy.selectedAttribute.choices;
  delete copy.operatorChoices;

  if (copy.selectedForm !== undefined){
    delete copy.selectedForm.attributes;

  }
  return copy;
}

function bucketModel(){
  'use strict'

  var self = this;

  self.conversions = ko.observableArray([new conversionModel()]);
}

function imputationModel(andOr){
  'use strict'

  var self = this;

  /* if the user is an and or 'or' operation
  limit the number of options as and/or nesting is not supported */
  self.operators = ko.pureComputed(function(){
    if(self.inAndOr()){
      return ['==', '!=', '>', '<', '>=', '<=']
    }
    else{
      return ['and', 'or', '==', '!=', '>', '<', '>=', '<=']
    }
  }, self);

  self.selectedOperator = ko.observable();
  self.selectedValue = ko.observable();
  self.inAndOr = ko.observable(andOr);

  //flag if logical operator is selected
  self.selectedLogical = ko.pureComputed(function(){
    if(['and', 'or'].indexOf(self.selectedOperator()) > -1){
      return true
    }
    else{
      return false
    }
  }, self);
}

function imputationViewModel(){
  'use strict';

  var self = this;

  self.conditions = ko.observableArray(['all', 'any']);
  self.selectedBucketComparison = ko.observable();
  self.selectedImputationComparison = ko.observable();
  self.imputations = ko.observableArray([]);

  self.confidence = ko.observable(1);

  self.isReady = ko.observableArray(false);
  self.isLoading = ko.observable(true);

  self.forms = ko.observableArray();
  self.buckets = ko.observableArray();

  self.drsc_forms = ko.observableArray();
  self.selectedDRSCForm = ko.observable();
  self.selectedDRSCAttribute = ko.observable();
  self.selectedMapTo = ko.observable();

  self.conversionLabel = ko.observable();
  self.imputationLabel = ko.observable();

  self.isSuccess = ko.observable(false);
  self.isDanger = ko.observable(false);
  self.msgType = ko.observable('Info - ');
  self.msg = ko.observable('Please wait until form loading is complete.');
  self.isInfo = ko.observable(true);

  self.addImputation = function(imputation){
    var andOr = false;

    if (self.imputations().length != 0){
      if(['and', 'or'].indexOf(imputation.selectedOperator())){
        andOr = true;
      }
    }

    var index = self.imputations.indexOf(imputation);
    self.imputations.splice(index + 1, 0, new imputationModel(andOr));

  }

  self.deleteImputation = function(imputation){
    self.imputations.remove(imputation);
  }

  self.addConversion = function(bucket){
    'use strict'

    var self = this;

    bucket.conversions.push(new conversionModel());
  }

  self.addBucket = function(bucket){
    'use strict'

    var index = self.buckets.indexOf(bucket);
    self.buckets.splice(index + 1, 0, new bucketModel());
  }

  self.removeBucket = function(bucket){
    'use strict'

    self.buckets.remove(bucket);
  }

  self.deleteConversion = function(bucket){
    'use strict'

    bucket.conversions.pop()
  }

  self.saveImputation = function(){
    'use strict'

    var noForm = false;

    ko.utils.arrayForEach(self.buckets(), function(bucket){
      ko.utils.arrayForEach(bucket.conversions(), function(conversion){
        if (conversion.selectedForm() === undefined){
          noForm = true;
        }
      });
    });

    if (noForm === true){
      self.isInfo(false);
      self.msgType('Error - ');
      self.msg('Please select a form for every variable operation.');
      self.isDanger(true);
    }

    else if (self.selectedDRSCForm() === undefined){
      self.isInfo(false);
      self.msgType('Error - ');
      self.msg('Please select a DRSC form to apply imputation.');
      self.isDanger(true);

      return;
    }


    else {

      var data = ko.toJSON({buckets: self.buckets(),
                            //get first conversion form to determine site on server
                            //this assumes all conversion are of the same site
                            site: self.buckets()[0].conversions()[0].selectedForm(),
                            maps_to: self.selectedMapTo(),
                            logical: self.logicalOperators(),
                            comparison: self.comparisonOperators(),
                            selected_comparison_condition: self.selectedComparisonCondition,
                            drsc: self.selectedDRSCForm(),
                            selected_drsc: self.selectedDRSCAttribute(),
                            confidence: self.confidence(),
                            conversion_label: self.conversionLabel(),
                            imputation_label: self.imputationLabel()
                            })

      //delete unnecessary data from the json
      data = JSON.parse(data);
      delete data.selected_drsc.choices;
      delete data.drsc.attributes;
      delete data.site.attributes;
      delete data.site.selectedAttribute;
      data = JSON.stringify(data);

      console.log(data);

/*      $.ajax({
        url: '/imports/mappings/imputation/map',
        method: 'POST',
        data: data,
        headers: {'X-CSRF-Token': $.cookie('csrf_token')},
        beforeSend: function(){
        },
        success: function(data, textStatus, jqXHR){
          window.location.href = '/imports';
        },
        complete: function(){
        }
      });*/
    }
  }

  self.select2SchemaParams = function(term, page){
    return {
      vocabulary: 'available_schemata',
      is_target: true,
      term: term
    };
  };

  self.select2SchemaResults = function(data){
    return {
        results: data.forms.map(function(value){
          return new formImputationModel(
            value.name, value.publish_date, value.attributes);
        })
    };
  };

  self.select2DRSCAttributeParams = function(term, page){
    return {
      vocabulary: 'available_attributes',
      schema: self.selectedDRSCForm().name,
      term: term
    };
  };

  self.select2DRSCAttributeResults = function(data){
    return {
        results: data.attributes.map(function(value){
          return new attributeImputationModel(
            value.variable, value.label, value.choices, value.datatype)
        })
    };
  };

  self.buckets.push(new bucketModel());
  self.isLoading(false);
}
