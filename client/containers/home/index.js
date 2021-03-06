import ko from 'knockout'
import Cookies from 'js-cookie'

import template from './index.html'

function imputationFormsModel(form, variable, mappedId){
  'use strict'

  var self = this;

  self.form = ko.observable(form);
  self.variable = ko.observable(variable);
  self.url = '/imports/mappings/view_mapped?id=' + mappedId;
}

function mappedModel(targetForm, targetVariable, study, studyForm,
                     studyVariable, dateMapped, mappedId, status, note){
  'use strict'

  var self = this;

  //set default values as imputations will have undefined values here
  studyForm = typeof studyForm !== 'undefined' ? studyForm : '';
  studyVariable = typeof studyVariable !== 'undefined' ? studyVariable : '';

  self.targetForm = ko.observable(targetForm);
  self.targetVariable = ko.observable(targetVariable);
  self.study = ko.observable(study);
  self.imputationForms = ko.observableArray([]);
  self.studyForm = ko.observable(studyForm);
  self.studyVariable = ko.observable(studyVariable);
  self.dateMapped = ko.observable(dateMapped);
  self.mappedId = ko.observable(mappedId);
  self.status = ko.observable(status);
  self.note = ko.observable(note);
  self.url = '/imports/mappings/view_mapped?id=' + mappedId;
  self.deleteRow = ko.observable(false);
}



function formListViewModel(){
  'use strict';

  var self = this;

  self.isReady = ko.observable(false);

  self.mapped = ko.observableArray();

  self.isDanger = ko.observable(false);
  self.isSuccess = ko.observable(false);
  self.msgType = ko.observable('');
  self.msg = ko.observable('');
  self.isInfo = ko.observable(false);

  self.numOfMappings = ko.observable(0);
  self.numOfDRSCMappings = ko.observable(0);
  self.filter = ko.observable();

  self.addDirectUrl = ko.observable()
  self.addImputationUrl = ko.observable()
  self.deleteUrl = ko.observable()

  self.canAdd = ko.pureComputed(() => {
    return !! (self.addDirectUrl() || self.addImputationUrl())
  })

  self.goToMapping = function(mapping){
      window.location.href = mapping.url;
  };

  self.sorts = {
    'targetForm asc': { field: 'targetForm', direction: 'asc'},
    'targetForm desc': { field: 'targetForm', direction: 'desc'},
    'targetVariable asc': { field: 'targetVariable', direction: 'asc'},
    'targetVariable desc': { field: 'targetVariable', direction: 'desc'},
    'study asc': { field: 'study', direction: 'asc'},
    'study desc': { field: 'study', direction: 'desc'},
    'studyForm asc': { field: 'studyForm', direction: 'asc'},
    'studyForm desc': { field: 'studyForm', direction: 'desc'},
    'studyVariable asc': { field: 'studyVariable', direction: 'asc'},
    'studyVariable desc': { field: 'studyVariable', direction: 'desc'},
    'dateMapped asc': { field: 'dateMapped', direction: 'asc'},
    'dateMapped desc': { field: 'dateMapped', direction: 'desc'},
    'status asc': { field: 'status', direction: 'asc'},
    'status desc': { field: 'status', direction: 'desc'},
  };

  self.sort = ko.observable(self.sorts['targetForm asc']);

  self.totalShowing  = ko.pureComputed(function(){
    return self.filteredMapped().length;
  });

  self.totalDRSCShowing  = ko.pureComputed(function(){
    self.vars = ko.utils.arrayMap(self.filteredMapped(), function(item){ return item.targetVariable()})

    return ko.utils.arrayGetDistinctValues(self.vars).length;
  });

  /**
   * Given a column name, determine the current sort type & order.
   */
  self.sortBy = function(columnName) {
      self.sort(self.sortForName(self.sort(),
          columnName, self.sorts));
  };

  //determine arrow type
  self.sortArrow =  function(columnName) {
    var arrow = '';
      if (columnName === self.sort().field) {
        if (self.sort().direction === 'asc') {
          arrow = 'fa fa-arrow-up fa-color';
        } else {
          arrow = 'fa fa-arrow-down fa-color';
        }
      }
      return arrow;
    },

  //obtain current sort
  self.sortForName = function(sort, columnName, allSorts) {
    var newSort;
      if (sort.field === columnName && sort.direction === 'asc') {
        newSort = allSorts[columnName+' desc'];
      } else {
        newSort = allSorts[columnName+' asc'];
      }
      return newSort;
    }

  // determine if box is checked
  // delete button only visible if at least one box is checked
  self.isChecked = ko.computed(function() {
      var count = 0;
      ko.utils.arrayForEach(self.mapped(), function(item) {
        if (item.deleteRow() == true){
          count += 1
        }
      });
      return count;
    });

  /**
   *  Filtered mappings based on filter string>
   */
  self.filteredMapped = ko.pureComputed(function(){
    var filter = self.filter();
    var asc = self.sort().direction === 'asc' ? true : false;

    // No filter, return mapped list
    if (!filter) {
      return self.mapped().sort(function (a, b) {
        // sort here
        var aprop = a[self.sort().field]();
        var bprop = b[self.sort().field]();
        if (asc) {
          return aprop > bprop ? 1 : -1;
        } else {
         return aprop < bprop ? 1 : -1;
        }
      });
    }

    // filter and sort mappings
    filter = filter.toLowerCase();

    return self.mapped().filter(function(mapping) {
      var formVarMatch = false;

      var matchFormOrVar = function(){
        return ko.utils.arrayFirst(mapping.imputationForms(), function(imputation){
          return imputation.form().toLowerCase().indexOf(filter) > -1
            || imputation.variable().toLowerCase().indexOf(filter) > -1
        });
      }

      if (mapping.imputationForms().length >= 1){
        formVarMatch = matchFormOrVar();
      }

      return formVarMatch
        || mapping.targetVariable().toLowerCase().indexOf(filter) > -1
        || mapping.targetForm().toLowerCase().indexOf(filter) > -1
        || mapping.study().toLowerCase().indexOf(filter) > -1
        || mapping.studyForm().toLowerCase().indexOf(filter) > -1
        || mapping.studyVariable().toLowerCase().indexOf(filter) > -1
        || mapping.dateMapped().toLowerCase().indexOf(filter) > -1
        || mapping.status().toLowerCase().indexOf(filter) > -1
      })
      .sort(function(a, b){
        var aprop = a[self.sort().field]();
        var bprop = b[self.sort().field]();
        if (asc) {
          return aprop > bprop ? 1 : -1;
        } else {
         return aprop < bprop ? 1 : -1;
        }
      });
  })

  self.deleteRows = function(){

    $.ajax({
      url: '/imports/mappings/delete',
      method: 'DELETE',
      data: ko.toJSON({mapped_delete: self.mapped()}),
      headers: {'X-CSRF-Token': Cookies.get('csrf_token')},
      beforeSend: function(){
      },
      success: function(data, textStatus, jqXHR){
        self.mapped.remove(function(item) { return item.deleteRow() == true })

        self.isInfo(false);
        self.isSuccess(true);
        self.msgType('Success - ');
        self.msg('All selected records deleted from database.');

        self.numOfMappings(self.mapped().length);
        self.vars = ko.utils.arrayMap(self.mapped(), function(item){ return item.targetVariable()})
        self.numOfDRSCMappings(ko.utils.arrayGetDistinctValues(self.vars).length);
      },
      error: function(data, textStatus, jqXHR){
        console.log(data.responseJSON);
        self.isInfo(false);
        self.isDanger(true);
        self.msgType('Error - ');
        self.msg('There was an error deleting record/s from the database.');
      },
      complete: function(){
      }
    });
  }

  // get initial data
  $.ajax({
    url: '/imports/mappings/view',
    method: 'GET',
    headers: {'X-CSRF-Token': Cookies.get('csrf_token')},
    beforeSend: function(){
    },
    success: function(data, textStatus, jqXHR){
      var json = data;

      self.addDirectUrl(data.$addDirectUrl)
      self.addImputationUrl(data.$addImputationUrl)
      self.deleteUrl(data.$deleteUrl)

      $.each(json.rows, function(){
        var row = new mappedModel(this.target_form, this.target_variable, this.study,
          this.study_form, this.study_variable, this.date_mapped,
          this.mapped_id, this.status, this.note);

        //if there are forms, this is an imputation and imputation
        //objects need to be instantiated
        //this supports multi line forms and variables in the view
        if (this.forms){
          var mappedId = this.mapped_id;
          $.each(this.forms, function(index, formData) {
            row.imputationForms.push(
              new imputationFormsModel(formData[0], formData[1], mappedId));
          });
        }
        self.mapped.push(row);
      });
    },
    complete: function(){
      self.numOfMappings(self.mapped().length);
      self.vars = ko.utils.arrayMap(self.mapped(), function(item){ return item.targetVariable()})
      self.numOfDRSCMappings(ko.utils.arrayGetDistinctValues(self.vars).length);
      self.isReady(true);
  }
  });
}

ko.components.register(
  'rl-home',
  {viewModel: formListViewModel, template: template}
)
