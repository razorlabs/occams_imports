function Choice (data){
  'use strict';

  var self = this;

  self.name = ko.observable();
  self.title = ko.observable();

  self.toString = ko.pureComputed(function(){
    return self.name() + ' - ' + self.title();
  });

  self.update = function(data) {
    data = data || {};
    self.name(data.name);
    self.title(data.title);
  };

  self.update(data);
}
