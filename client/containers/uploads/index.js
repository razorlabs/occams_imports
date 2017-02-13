import ko from 'knockout'
import template from './index.html'
import {Project} from 'services'
import {Upload} from 'services'
import 'bindings/modal'


class Error {

  constructor (date, message) {
    this.date = date
    this.message = message
  }
}

export default class UploadsView {

  /**
   * Create a project detail view
   */
  constructor(params) {

    this.isReady = ko.observable(false)
    this.projects = ko.observableArray([])
    this.hasProjects = ko.pureComputed(() => this.projects().length > 0)
    this.selectedProject = ko.observable(null)

    Project.query()
      .then( projects => {
        this.projects(projects.filter(project => project.title() != 'DRSC'))
        if (this.hasProjects()){
          this.selectedProject(this.projects()[0]);
        }
      })

  }

}

ko.components.register(
  'rl-uploads',
  {
    viewModel: UploadsView,
    template: template
  }
)
