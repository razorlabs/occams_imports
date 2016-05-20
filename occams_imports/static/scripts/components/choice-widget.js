function ChoiceWidgetView(params){
  'use strict';
  var self = this;

  self.schema = params.schema;
  self.attribute = params.attribute;
  self.choice = params.choice;

  self.queryChoiceData = function(term, page){
    return {
      vocabulary: 'available_choices',
      schema: self.schema().name(),
      attribute: self.attribute().name(),
      term: term
    };
  };

  self.parseChoiceResults = function(data){
    return {
        results: data.choices.map(function(value){
          return new Choice(value);
        })
    };
  };
}

ko.components.register('choice-widget', {
    viewModel: ChoiceWidgetView,
    template: {element: 'choice-widget-template'},
})
