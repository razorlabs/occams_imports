function Schema (data){
  'use strict';
  var self = this;

  self.name = ko.observable();
  self.title = ko.observable();
  self.publish_date = ko.observable();

  self.update = function(data){
    data = data || {};
    self.name(data.name);
    self.title(data.title);
    self.publish_date(data.publish_date);
  };

  self.update(data);
}

