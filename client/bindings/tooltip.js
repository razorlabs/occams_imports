import ko from 'knockout'

ko.bindingHandlers.tooltip = {
  init: (element, valueAccessor) => {
    let local = ko.utils.unwrapObservable(valueAccessor()),
        options = {}

    ko.utils.extend(options, ko.bindingHandlers.tooltip.options)
    ko.utils.extend(options, local)

    $(element).tooltip(options)

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      $(element).tooltip('destroy')
    })
  },
  options: {
    placement: 'right',
    trigger: 'hover'
  }
}
