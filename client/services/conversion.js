import ko from 'knockout'

import Variable from './variable'

export default class Conversion {

  constructor (data) {
    this.operator = ko.observable()
    this.value = ko.observable()

    this.byVariable = ko.pureComputed(() => this.value() instanceof Variable)
    this.byValue = ko.pureComputed(() => !this.byVariable())

    this.update(data)
  }

  changeType (data, event) {
    this.value(event.target.value == 'VAR' ? new Variable() : null)
  }

  update (data) {
    data = data || {}
    this.operator(data.operator)
    if (typeof data.value === 'object'){
      this.value(new Variable(data.value))
    } else {
      this.value(data.value)
    }
  }

}
