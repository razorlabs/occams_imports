import ko from 'knockout'

import Conversion from './conversion'
import Group from './group'
import ImputationList from './condition'
import Variable from './variable'

export default class Mapping {

  constructor(data) {
    this.description = ko.observable('')

    this.target = ko.observable()
    this.targetChoice = ko.observable()
    this.condition = ko.observable('ALL')
    this.groups = ko.observableArray([])

    this.condition.subscribe((newValue) => {
      if (newValue != 'ALL' && newValue != 'ANY'){
        this.condition('ALL')
      }
    })

    this.groupsLength = ko.pureComputed(() => this.groups().length)
    this.hasMultipleGroups = ko.pureComputed(() => this.groupsLength() > 1)

    this.update(data)
  }

  addGroup () {
    var initialVariable = new Variable()
      , initialConversion = new Conversion()
      , initialLogic = new ImputationList()
      , group = new Group()

    initialConversion.value(initialVariable)
    group.conversions.push(initialConversion)
    group.logic(initialLogic)
    this.groups.push(group)
  }

  copyGroup (group) {
    var data = ko.toJS(group),
        copy = new Group(data),
        index = this.groups.indexOf(group)

    this.groups.splice(index + 1, 0, copy)
  }

  removeGroup (group) {
    this.groups.remove(group)
  }

  update (data) {
    data = data || {}
    this.target(new Variable(data.target))
    this.condition(data.condition)
    this.groups((data.groups || []).map(function(value){
      return new Group(value)
    }))
  }
}
