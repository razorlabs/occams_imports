function Variable (data){
  'use strict';
  var self = this;

  self.schema = ko.observable();
  self.attribute = ko.observable();

  self.update = function(data){
    data = data || {};
    self.schema(data.schema ? new Schema(data.schema) : null);
    self.attribute(data.attribute ? new Attribute(data.attribute) : null);
  };

  self.update(data);
}
