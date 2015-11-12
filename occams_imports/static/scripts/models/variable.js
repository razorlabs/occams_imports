function Variable (data){
  'use strict';
  var self = this;

  self.schema = ko.observable();
  self.attribute = ko.observable();

  // Avoid mismatching schema/attributes by reseting if new schema is used
  self.schema.subscribe(function(schema){
    self.attribute(null);
  });

  self.update = function(data){
    data = data || {};
    self.schema(data.schema ? new Schema(data.schema) : null);
    self.attribute(data.attribute ? new Attribute(data.attribute) : null);
  };

  self.update(data);
}
