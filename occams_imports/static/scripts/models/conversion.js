function Conversion (data){
  'use strict';

  var self = this;

  self.operator = ko.observable();
  self.value = ko.observable();

  self.byVariable = ko.pureComputed(function(){
    var value = self.value();
    return value && value instanceof Variable;
  });

  self.byValue = ko.pureComputed(function(){
    var value = self.value();
    return value && !(value instanceof Variable);
  });

  self.update = function(data){
    data = data || {};
    self.operator(data.operator);
    if (typeof data.value === 'object'){
      self.value(new Variable(data.value));
    } else {
      self.value(data.value);
    }
  };

  self.toJSON = function(){
    var copy = ko.toJS(self);
    delete copy.mathOperators;
    delete copy.selectedAttribute.label;
    delete copy.selectedAttribute.choices;
    delete copy.operatorChoices;

    if (copy.selectedForm !== undefined){
      delete copy.selectedForm.attributes;
    }
    return copy;
  };

  self.update(data);

  //self.select2AttributeParams = function(term, page){
    //return {
      //vocabulary: 'available_attributes',
      //schema: self.selectedForm().name,
      //term: term
    //};
  //};

  //self.select2AttributeResults = function(data){
    //return {
        //results: data.attributes.map(function(value){
          //return new attributeImputationModel(
            //value.variable, value.label, value.choices, value.datatype)
        //})
    //};
  //};

  //self.select2SchemaParams = function(term, page){
    //return {
      //vocabulary: 'available_schemata',
      //is_target: false,
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
}
