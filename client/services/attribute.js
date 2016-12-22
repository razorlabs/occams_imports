import ko from 'knockout'

export default class Attribute {

  constructor (data) {
    this.name = ko.observable();
    this.title = ko.observable();
    this.type = ko.observable();

    this.hasChoices = ko.pureComputed(() => this.type() == 'choice')

    this.update(data)
  }

  update (data) {
    data = data || {};
    this.name(data.name);
    this.title(data.title);
    this.type(data.type);
  };

}

