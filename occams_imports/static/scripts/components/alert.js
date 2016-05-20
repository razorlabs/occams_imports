function AlertComponent(data){
  'use strict';
  var self = this;
  self.type = data.type;
  self.title = data.title;
  self.message = data.message;
  self.css = {
    'js-alert': true,
    'alert': true,
    'alert-success': self.type === 'sucess',
    'alert-info': self.type === 'info',
    'alert-warning': self.type === 'warning',
    'alert-danger': self.type === 'error' || self.type === 'danger',
  };
}
