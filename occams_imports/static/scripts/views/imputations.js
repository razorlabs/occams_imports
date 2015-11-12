function MappingView(data){
  'use strict';
  var self = this;

  self.isReady = ko.observableArray(false);
  self.isLoading = ko.observable(false);

  self.alert = ko.observable();

  self.mapping = new Mapping();

  self.saveMapping = function(){

    var data = ko.toJSON(self.mapping);
    console.log('Sending data:', data);

    $.ajax({
      url: window.location,
      method: 'POST',
      data: data,
      headers: {'X-CSRF-Token': $.cookie('csrf_token')},
      beforeSend: function(){
        self.alert(null);
        self.isLoading(true);
      },
      success: function(data, textStatus, jqXHR){
        window.location.href = data.__next__
      },
      complete: function(){
        self.isLoading(false);
      }
    });
  }

  self.isReady(true);
}
