import ko from 'knockout'
import $ from 'jquery'

import 'bootstrap-sass/assets/javascripts/bootstrap/modal'

ko.bindingHandlers.modalVisible = {
  init: function (element, valueAccessor) {
    let value = valueAccessor()

    $(element).modal({show: false})

    if (ko.isObservable(value)) {
      $(element).on('hide.bs.modal', () => value(null))
    }
  },
  update: (element, valueAccessor) => {
    let show = !!ko.unwrap(valueAccessor()),
        action = show ? 'show': 'hide'
    $(element).modal(action)
  }
}

