function mappedViewModel(){
  'use strict';

  var self = this;

  self.isReady = ko.observable(false);
  self.selectedStatus = ko.observable();
  self.note = ko.observable('');
  self.msg = ko.observable();
  self.isSuccess = ko.observable();
  self.isDanger = ko.observable();

  self.statusLevel = ko.computed(function() {
    var statusType = self.selectedStatus();
    if (statusType == 'review'){
      return 'label-warning'
    }
    else if (statusType == 'in-progress'){
      return 'label-primary'
    }
    else if (statusType == 'approved'){
      return 'label-success'
    }
    else if (statusType == 'rejected'){
      return 'label-danger'
    }
  });

  var url = function(){
    var queryString = window.location.search;
    var mappingID = queryString.split('=')[1];
    var baseURL = '/imports/mapping/status?id=';

    return baseURL + mappingID
  };

  var urlNotes = function(){
    var queryString = window.location.search;
    var mappingID = queryString.split('=')[1];
    var baseURL = '/imports/mapping/notes?id=';

    return baseURL + mappingID
  };

  self.updateStatus = function(){
    var data = self.selectedStatus();
    console.log('Sending data:', data);
    $.ajax({
      url: url(),
      method: 'PUT',
      data: JSON.stringify({'status': data}),
      headers: {'X-CSRF-Token': $.cookie('csrf_token'), contentType: 'application/json; charset=utf-8'},
      beforeSend: function(){
      },
      success: function(data, textStatus, jqXHR){
        self.isDanger(false);
        self.isSuccess(true);
        self.msg('Status successfully updated in the database.')
      },
      error: function(data, textStatus, jqXHR){
        self.isSuccess(false);
        self.isDanger(true);
        self.msg('There was an error updating the status in the database.  Status Code: ' + data.status + ' - ' + data.statusText);
      },
      complete: function(){
    }
    });
  };

  self.updateNotes = function(){
    var data = self.note();
    console.log('Sending data:', data);
    $.ajax({
      url: urlNotes(),
      method: 'PUT',
      data: JSON.stringify({'notes': data}),
      headers: {'X-CSRF-Token': $.cookie('csrf_token'), contentType: 'application/json; charset=utf-8'},
      beforeSend: function(){
      },
      success: function(data, textStatus, jqXHR){
        self.isDanger(false);
        self.isSuccess(true);
        self.msg('Your note was successfully updated in the database.')
      },
      error: function(data, textStatus, jqXHR){
        self.isSuccess(false);
        self.isDanger(true);
        self.msg('There was an error updating your note in the database.  Status Code: ' + data.status + ' - ' + data.statusText);
      },
      complete: function(){
    }
    });
  };

  // get the initial status level and notes
  $.ajax({
    url: url(),
    method: 'GET',
    headers: {'X-CSRF-Token': $.cookie('csrf_token')},
    beforeSend: function(){
    },
    success: function(data, textStatus, jqXHR){
      var status = data.status;
      var notes = data.notes;

      self.selectedStatus(status);
      self.note(notes);

    },
    complete: function(){
      self.isReady(true);
  }
  });
}