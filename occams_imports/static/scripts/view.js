function imputationFormsModel(form, variable){
  'use strict'

  var self = this;

  self.form = ko.observable(form);
  self.variable = ko.observable(variable);
}

function mappedModel(targetForm, targetVariable, study, studyForm,
                     studyVariable, dateMapped, mappedId, status){
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
  self.url = '/imports/mappings/view_mapped?id=' + mappedId;
  self.deleteRow = ko.observable(false);
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
  self.numOfDRSCMappings = ko.observable(0);
  self.filter = ko.observable();

  self.totalShowing  = ko.pureComputed(function(){
    return self.filteredMapped().length;
  });

  self.totalDRSCShowing  = ko.pureComputed(function(){
    self.vars = ko.utils.arrayMap(self.filteredMapped(), function(item){ return item.targetVariable()})

    return ko.utils.arrayGetDistinctValues(self.vars).length;
  });

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

    // No filter, return mapped list
    if (!filter) {
      return self.mapped().sort(function (a, b) {
        return a.targetVariable().toLowerCase() > b.targetVariable().toLowerCase()  ? 1 : -1;
      });
    }

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
      });
  })

  // get initial data
  $.ajax({
    url: '/imports/mappings/view',
    method: 'GET',
    headers: {'X-CSRF-Token': $.cookie('csrf_token')},
    beforeSend: function(){
    },
    success: function(data, textStatus, jqXHR){
      var json = data;

      $.each(json.rows, function(){
        var row = new mappedModel(this.target_form, this.target_variable, this.study,
          this.study_form, this.study_variable, this.date_mapped,
          this.mapped_id, this.status);

        //if there are forms, this is an imputation and imputation
        //objects need to be instantiated
        //this supports multi line forms and variables in the view
        if (this.forms){
          $.each(this.forms, function(index, formData) {
            row.imputationForms.push(
              new imputationFormsModel(formData[0], formData[1]));
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
