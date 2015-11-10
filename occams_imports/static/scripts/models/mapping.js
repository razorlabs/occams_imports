function Mapping(data){
  'use strict';

  var self = this;

  self.title = ko.observable();
  self.description = ko.observable();

  self.target = ko.observable();
  self.confidence = ko.observable();
  self.condition = ko.observable('ALL');
  self.groups = ko.observableArray();

  self.groupsLength = ko.pureComputed(function(){
    return self.groups().length;
  });

  self.hasMultipleGroups = ko.pureComputed(function(){
    return self.groupsLength() > 1;
  });

  self.update = function(data){
    data = data || {};
    self.target(new Variable(data.target));
    self.confidence(data.conversion);
    self.condition(data.condition);
    self.groups((data.groups || []).map(function(value){
      return new Group(value);
    }));
  }

  self.update(data);
}
