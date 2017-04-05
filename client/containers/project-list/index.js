import ko from 'knockout'

import {Project} from 'services'
import 'containers/project-detail'
import template from './index.html'

/**
 * Container for project list overview
 */
export default class ProjectListView {

  constructor () {

    this.isReady = ko.observable(false)

    this.projects = ko.observableArray([])
    this.hasProjects = ko.pureComputed(() => this.projects().length > 0)

    this.selectedProject = ko.observable()

    Project.query().then( projects => {
      this.projects(projects)
      this.isReady(true)
    })
  }

  selectProject (project) {
    this.selectedProject(project)
  }

}


ko.components.register(
  'rl-project-list',
  {
    template: template,
    viewModel: ProjectListView
  }
)
