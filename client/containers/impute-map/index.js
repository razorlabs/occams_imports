import ko from 'knockout'
import Cookies from 'js-cookie'
import {Mapping} from 'services'
import 'components/choice-widget'
import 'components/variable-widget'
import template from './index.html'


function MappingView(data){
  'use strict'
  var self = this

  self.isReady = ko.observableArray(false)
  self.isLoading = ko.observable(false)

  self.mapping = new Mapping()

  self.saveMapping = function(){

    var data = ko.toJSON(self.mapping)
    console.log('Sending data:', data)

    $.ajax({
      url: window.location,
      method: 'POST',
      data: data,
      headers: {'X-CSRF-Token': Cookies.get('csrf_token')},
      beforeSend: function(){
        self.isLoading(true)
      },
      success: function(data, textStatus, jqXHR){
        window.location.href = data.__next__
      },
      complete: function(){
        self.isLoading(false)
      }
    })
  }

  self.isReady(true)
}

ko.components.register(
  'rl-impute-map',
  {
    viewModel: MappingView,
    template: template
  }
)
