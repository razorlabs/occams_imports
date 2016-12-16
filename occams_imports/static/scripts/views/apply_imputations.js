/**
 * View model for applying imputations
 */
function ImputationViewModel(options) {
  var self = this;

  self.isDanger = ko.observable(false);
  self.isSuccess = ko.observable(false);
  self.isInfo = ko.observable(true);
  self.msg = ko.observable('');

  self.count = ko.observable(0);
  self.total = ko.observable(0);

  /**
   * Calculates this the mappings' current progress
   */
  self.progress = ko.pureComputed(function(){
    result = Math.ceil((self.count() / self.total()) * 100);

    if (result === 100) {
      self.msg(self.total() + ' Mappings successfully processed.');
      self.isInfo(false);
      self.isSuccess(true);
    }

    return result;
  }).extend({ throttle: 1 });

  self.widthPercentage = ko.pureComputed(function(){
    return self.progress() + '%';
  });

  self.statusPercentageLabel = ko.pureComputed(function(){
    return self.progress() + '% Complete (success)';
  });

  +function(){

    var source = new EventSource(options.notifications_url);

    source.addEventListener('progress', function(event){
      var data = JSON.parse(event.data);

      self.count(data['count']);
      self.total(data['total'])
    });

    $.ajax({
      url: options.imputation_mappings_url,
      method: 'GET',
      headers: {'X-CSRF-Token': $.cookie('csrf_token')},
      beforeSend: function(){
        self.msg('Sending request to process mappings.');
      },
      success: function(data, textStatus, jqXHR){
        self.msg('Mappings in progress.');
      },
      complete: function(){
    }
    });

  }();

}