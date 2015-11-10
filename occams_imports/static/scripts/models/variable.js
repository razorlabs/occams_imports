function Variable (data){
  'use strict';

  var self = this;

  self.schema = ko.observable();
  self.attribute = ko.observable();
  self.choice = ko.observable();

  self.update = function(data){
    data = data || {};
    self.schema(new Schema(data.schema));
    self.attribute(new Attribute(data.attribute));
    self.choice(new Choice(data.choice));
  };

  self.update(data);
}
