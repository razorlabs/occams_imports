import ko from 'knockout'
import pathToRegexp from 'path-to-regexp'

import checkStatus from 'utilities/fetch/checkStatus'

import template from './index.html'


const CHANNEL = 'mapping'
const JOBS_URI = '/imports/api/jobs'
const PROGRESS_URI = '/imports/api/progress'

/**
 * View model for applying imputations
 */

class ApplyMapViewModel {


  constructor() {
    this.notifications = ko.observableArray([])
    this.count = ko.observable(0)
    this.total = ko.observable(0)

    /**
     * Calculates this the mappings' current progress
     */
    this.progress = ko.pureComputed(() => {
      return Math.ceil((this.count() / this.total()) * 100)
    }).extend({throttle: 1})

    this.progressStatus = ko.pureComputed(() => {
      return this.progress() == 100 ? 'success' : 'info'
    })

    this.pubsub = new EventSource(NOTIFICATIONS_URI)
    this.pubsub.addEventListener(CHANNEL, event => {
      let data = JSON.parse(event.data)
      this.count(data['count'])
      this.total(data['total'])
    })

    this.notifications.push('Sending request to process mappings.')

    fetch(MAPPINGS_URI, {credentials: 'include'})
    .then(checkStatus)
    .then(response => this.notifiations.push('Mappings in progress.'))
  }

}

ko.components.register('rl-apply-amp', {
  viewModel: ApplyMapViewModel,
  template: template
})
