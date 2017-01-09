import ko from 'knockout'

import 'bindings/select2'
import {Schema, Attribute} from 'services'
import template from './index.html'

function VariableComponent(params){
  'use strict';
  var self = this;

  self.isTarget = params.isTarget;
  self.variable = params.variable;

  self.nextSchemaSearch  = function(variable, term){
    var schema = self.variable().schema();
    return schema ? schema.name() : null;
  };

  self.nextAttributeSearch = function(variable, term){
    var attribute = self.variable().attribute();
    return attribute? attribute.name() : null;
  };

  self.querySchemaData = function(term, page){
    return {
      vocabulary: 'available_schemata',
      is_target: self.isTarget,
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
      schema: self.variable().schema().name(),
      term: term
    };
  };

  self.parseAttributeResults = function(data){
    return {
        results: data.attributes.map(function(value){
          return new Attribute(value);
        })
    };
  };
}

ko.components.register(
  'variable-widget',
  { viewModel: VariableComponent, template: template }
)
