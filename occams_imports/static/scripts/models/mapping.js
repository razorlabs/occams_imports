function Mapping(data){
  'use strict';
  var self = this;

  self.description = ko.observable();

  self.target = ko.observable();
  self.targetChoice = ko.observable();
  self.confidence = ko.observable();
  self.condition = ko.observable('ALL');
  self.groups = ko.observableArray();

  self.condition.subscribe(function(newValue){
    if (newValue != 'ALL' && newValue != 'ANY'){
      self.condition('ALL');
    }
  });

  self.groupsLength = ko.pureComputed(function(){
    return self.groups().length;
  });

  self.hasMultipleGroups = ko.pureComputed(function(){
    return self.groupsLength() > 1;
  });

  self.addGroup = function(){
    var initialVariable = new Variable()
      , initialConversion = new Conversion()
      , initialLogic = new ImputationList()
      , group = new Group();

    initialConversion.value(initialVariable);
    group.conversions.push(initialConversion);
    group.logic(initialLogic);
    self.groups.push(group);
  };

  self.copyGroup = function(group){
    var data = ko.toJS(group),
        copy = new Group(data),
        index = self.groups.indexOf(group)
        ;
    self.groups.splice(index + 1, 0, copy);
  }

  self.removeGroup = function(group){
    self.groups.remove(group);
  };

  self.update = function(data){
    data = data || {};
    self.target(new Variable(data.target));
    self.confidence(data.confidence);
    self.condition(data.condition);
    self.groups((data.groups || []).map(function(value){
      return new Group(value);
    }));
  }

  self.update(data);
}
