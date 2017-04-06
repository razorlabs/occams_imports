import ko from 'knockout'
import {Project} from 'services'
import {Upload} from 'services'
import 'bindings/modal'

import checkStatus from 'utilities/fetch/checkStatus'

import template from './index.html'

const PROCESS_URI = '/imports/api/process'
const STATUS_URI = '/imports/api/process/status'


class Error {

  constructor (date, message) {
    this.date = date
    this.message = message
  }
}


export default class ProcessView {

  /**
   * Create a project detail view
   */
  constructor(params) {

    this.isReady = ko.observable(false)
    this.projects = ko.observableArray([])
    this.hasProjects = ko.pureComputed(() => this.projects().length > 0)
    this.selectedProject = ko.observable(null)

    this.notifications = ko.observableArray([])
    this.count = ko.observable(0)
    this.total = ko.observable(0)

    /**
     * Calculates this the mappings' current progress
     */
    this.progress = ko.pureComputed(() => {
      return Math.ceil((this.count() / this.total()) * 100)
    }).extend({throttle: 1})

    this.progressWidth = ko.pureComputed( () => `${this.progress()}%` )

    this.isProcessing = ko.pureComputed( () => this.progress() < 100 )

    this.progressStatus = ko.pureComputed(() => {
      return this.progress() == 100 ? 'success' : 'info'
    })

    this.pubsub = new EventSource(STATUS_URI)

    this.pubsub.addEventListener('progress', event => {
      let data = JSON.parse(event.data)
      this.count(data['count'])
      this.total(data['total'])
      console.log(this.progress())
    })

    this.pubsub.addEventListener('message', event => {
      let {variable, message} = JSON.parse(event.data)
      console.log(message)
      this.notifications.push(`${variable} -- ${message}`)
    })

    this.notifications.push('Sending request to process mappings.')

    Project.query()
      .then( projects => {
        this.projects(projects.filter(project => project.title() != 'DRSC'))
        if (this.hasProjects()){
          this.selectedProject(this.projects()[0]);
        }
      })

  }

}

ko.components.register('rl-process', {
  viewModel: ProcessView,
  template: template
})

