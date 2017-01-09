import ko from 'knockout'

import {Table} from 'services'
import template from './index.html'


export default class ProjectDetailView{

  /**
   * Create a project detail view
   */
  constructor(params) {

    this.project = params.project

    this.isReady = ko.observable(false)
    this.tables = ko.observableArray([])
    this.hasTables = ko.pureComputed(() => this.tables().length > 0)

    Table.query({projectName: this.project.name()})
      .then( tables => {
        this.tables(tables)
        this.sortTablesByName()
        this.isReady(true)
      })
  }

  /**
   * Sort the current listing of tables in place by name
   */
  sortTablesByName () {
    this.tables.sort((a, b) => a.name().localeCompare(b.name()))
  }

}


ko.components.register(
  'rl-project-detail',
  {
    template: template,
    viewModel: ProjectDetailView
  }
)
