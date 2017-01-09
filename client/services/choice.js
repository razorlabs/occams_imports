import ko from 'knockout'

export default class Choice {

  constructor (data) {
    this.name = ko.observable();
    this.title = ko.observable();

    this.toString = ko.pureComputed(() => `${this.name()} - ${this.title()}`)

    this.update(data);
  }

  update (data) {
    data = data || {};
    this.name(data.name);
    this.title(data.title);
  };

}
