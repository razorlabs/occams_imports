function MappingView(data){

  'use strict';

  var self = this;

  self.isReady = ko.observableArray(false);
  self.isLoading = ko.observable(false);

  self.alert = ko.observable();

  self.mapping = new Mapping();

  //self.addImputation = function(imputation){
    //var andOr = false;

    //if (self.imputations().length != 0){
      //if(['and', 'or'].indexOf(imputation.selectedOperator())){
        //andOr = true;
      //}
    //}

    //var index = self.imputations.indexOf(imputation);
    //self.imputations.splice(index + 1, 0, new imputationModel(andOr));

  //}

  //self.deleteImputation = function(imputation){
    //self.imputations.remove(imputation);
  //}

  //self.addConversion = function(bucket){
    //'use strict'

    //var self = this;

    //bucket.conversions.push(new conversionModel());
  //}

  //self.addBucket = function(bucket){
    //'use strict'

    //var index = self.buckets.indexOf(bucket);
    //self.buckets.splice(index + 1, 0, new bucketModel());
  //}

  //self.removeBucket = function(bucket){
    //'use strict'

    //self.buckets.remove(bucket);
  //}

  //self.deleteConversion = function(bucket){
    //'use strict'

    //bucket.conversions.pop()
  //}

  //self.saveImputation = function(){
    //'use strict'

    //var noForm = false;

    //ko.utils.arrayForEach(self.buckets(), function(bucket){
      //ko.utils.arrayForEach(bucket.conversions(), function(conversion){
        //if (conversion.selectedForm() === undefined){
          //noForm = true;
        //}
      //});
    //});

    //if (noForm === true){
      //self.isInfo(false);
      //self.msgType('Error - ');
      //self.msg('Please select a form for every variable operation.');
      //self.isDanger(true);
    //}

    //else if (self.selectedDRSCForm() === undefined){
      //self.isInfo(false);
      //self.msgType('Error - ');
      //self.msg('Please select a DRSC form to apply imputation.');
      //self.isDanger(true);

      //return;
    //}


    //else {

      //var data = ko.toJSON({buckets: self.buckets(),
                            ////get first conversion form to determine site on server
                            ////this assumes all conversion are of the same site
                            //site: self.buckets()[0].conversions()[0].selectedForm(),
                            //maps_to: self.selectedMapTo(),
                            //logical: self.logicalOperators(),
                            //comparison: self.comparisonOperators(),
                            //selected_comparison_condition: self.selectedComparisonCondition,
                            //drsc: self.selectedDRSCForm(),
                            //selected_drsc: self.selectedDRSCAttribute(),
                            //confidence: self.confidence(),
                            //conversion_label: self.conversionLabel(),
                            //imputation_label: self.imputationLabel()
                            //})

      ////delete unnecessary data from the json
      //data = JSON.parse(data);
      //delete data.selected_drsc.choices;
      //delete data.drsc.attributes;
      //delete data.site.attributes;
      //delete data.site.selectedAttribute;
      //data = JSON.stringify(data);

      //console.log(data);

//[>      $.ajax({
        //url: '/imports/mappings/imputation/map',
        //method: 'POST',
        //data: data,
        //headers: {'X-CSRF-Token': $.cookie('csrf_token')},
        //beforeSend: function(){
        //},
        //success: function(data, textStatus, jqXHR){
          //window.location.href = '/imports';
        //},
        //complete: function(){
        //}
      //});*/
    //}
  //}

  //self.select2SchemaParams = function(term, page){
    //return {
      //vocabulary: 'available_schemata',
      //is_target: true,
      //term: term
    //};
  //};

  //self.select2SchemaResults = function(data){
    //return {
        //results: data.forms.map(function(value){
          //return new formImputationModel(
            //value.name, value.publish_date, value.attributes);
        //})
    //};
  //};

  //self.select2DRSCAttributeParams = function(term, page){
    //return {
      //vocabulary: 'available_attributes',
      //schema: self.selectedDRSCForm().name,
      //term: term
    //};
  //};

  //self.select2DRSCAttributeResults = function(data){
    //return {
        //results: data.attributes.map(function(value){
          //return new attributeImputationModel(
            //value.variable, value.label, value.choices, value.datatype)
        //})
    //};
  //};

  //self.buckets.push(new bucketModel());
  //self.isLoading(false);
  //

  self.querySchemaData = function(term, page){
    return {
      vocabulary: 'available_schemata',
      term: term
    };
  };

  self.parseSchemaResults = function(data){
    return {
        results: data.schemata.map(function(value){
          return new Schema(value);
        })
    };
  };

  self.queryAttributeData = function(term, page){
    return {
      vocabulary: 'available_attributes',
      schema: self.mapping().schema().name,
      term: term
    };
  };

  self.queryAttributeDataFor = function(schema_name){
    console.log(schema_name);
    return function(term, page){
      return {
        vocabulary: 'available_attributes',
        schema: schema_name,
        term: term
      };
    };
  }

  self.parseAttributeResults = function(data){
    return {
        results: data.attributes.map(function(value){
          return new Attribuet(value);
        })
    };
  };

  self.isReady(true);
}
