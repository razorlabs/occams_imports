import ko from 'knockout'

import Schema from './schema'
import Attribute from './attribute'

export default class Variable {

  constructor (data) {
    this.schema = ko.observable();
    this.attribute = ko.observable();

    // Avoid mismatching schema/attributes by reseting if new schema is used
    this.schema.subscribe((schema) => this.attribute(null))

    this.update(data);
  }

  update (data) {
    data = data || {};
    this.schema(data.schema ? new Schema(data.schema) : null);
    this.attribute(data.attribute ? new Attribute(data.attribute) : null);
  };

}
