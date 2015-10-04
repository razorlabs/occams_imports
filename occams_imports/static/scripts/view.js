function mappedModel(drsc_form, drsc_variable, site_form,
                     site_variable, date_mapped, mapped_id){
  'use strict'

  var self = this;

  self.drsc_form = ko.observable(drsc_form);
  self.drsc_variable = ko.observable(drsc_variable);
  self.site_form = ko.observable(site_form);
  self.site_variable = ko.observable(site_variable);
  self.date_mapped = ko.observable(date_mapped);
  self.mapped_id = ko.observable(mapped_id);
  self.url = '/imports/mappings/view_mapped?id=' + mapped_id;
  self.deleteRow = ko.observable(false);
}

function viewMappedVariable(mapped){
  'use strict'

  var self = this;

  $.ajax({
    url: '/imports/mappings/view_mapped',
    method: 'POST',
    data: ko.toJSON({mapped_id: mapped.mapped_id}),
    headers: {'X-CSRF-Token': $.cookie('csrf_token')},
    beforeSend: function(){
    },
    success: function(data, textStatus, jqXHR){

    },
    complete: function(){
    }
  });
}

function deleteRows(){
  'use strict'

  var self = this;

  $.ajax({
    url: '/imports/mappings/delete',
    method: 'DELETE',
    data: ko.toJSON({mapped_delete: self.mapped()}),
    headers: {'X-CSRF-Token': $.cookie('csrf_token')},
    beforeSend: function(){
    },
    success: function(data, textStatus, jqXHR){
      self.mapped.remove(function(item) { return item.deleteRow() == true })

      self.isInfo(false);
      self.isSuccess(true);
      self.msgType('Success - ');
      self.msg('All selected records deleted from database.');
    },
    complete: function(){
    }
  });

}

function formListViewModel(){
  'use strict';

  var self = this;

  self.isReady = ko.observable(false);

  self.mapped = ko.observableArray();

  self.isDanger = ko.observable(false);
  self.isSuccess = ko.observable(false);
  self.msgType = ko.observable('Info - ');
  self.msg = ko.observable('Please click chevron on the right to view mapping.');
  self.isInfo = ko.observable(true);

  self.numOfMappings = ko.observable(0);

  self.isChecked = ko.computed(function() {
      var count = 0;
      ko.utils.arrayForEach(self.mapped(), function(item) {
        if (item.deleteRow() == true){
          count += 1
        }
      });
      return count;
    });

  $.ajax({
    url: '/imports/mappings/view',
    method: 'GET',
    headers: {'X-CSRF-Token': $.cookie('csrf_token')},
    beforeSend: function(){
    },
    success: function(data, textStatus, jqXHR){
      var json = $.parseJSON(data);

      $.each(json.rows, function(){
        var row = new mappedModel(this.drsc_form, this.drsc_variable,
          this.site_form, this.site_variable, this.date_mapped,
          this.mapped_id);

        self.mapped.push(row);

      });
    },
    complete: function(){
      self.numOfMappings(self.mapped().length);
      self.isReady(true);
  }
  });
}