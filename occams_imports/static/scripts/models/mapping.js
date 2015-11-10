function Mapping(data){
  'use strict';

  var self = this;

  self.availableOperators = LOGICAL;

  self.title = ko.observable();
  self.description = ko.observable();

  self.target = ko.observable();
  self.confidence = ko.observable();
  self.condition = ko.observable(ALL);
  self.buckets = ko.observableArray();

  self.bucketsLength = ko.pureComputed(function(){
    return self.buckets().length;
  });

  self.hasMultipleBuckets = ko.pureComputed(function(){
    return self.bucketsLength() > 1;
  });

  self.update = function(data){
    data = data || {};
    self.target(new Variable(data.target));
    self.confidence(data.conversion);
    self.condition(data.condition);
    self.buckets((data.buckets || []).map(function(value){
      return new Bucket(value);
    }));
  }

  self.update(data);
}
