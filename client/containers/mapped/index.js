import ko from 'knockout'
import Cookies from 'js-cookie'

import checkStatus from 'utilities/fetch/checkStatus'
import template from './index.html'


class MappingView {

  constructor() {
    this.mapping = ko.observable()
    this.canApprove = ko.pureComputed(() => (this.mapping() || {}).$approveUrl)

    this.isReady = ko.observable(false)

    this.selectedStatus = ko.observable()

    this.note = ko.observable('')
    this.msg = ko.observable()

    this.isSuccess = ko.observable()
    this.isDanger = ko.observable()

    this.statusLevel = ko.pureComputed(() => {
      switch( this.selectedStatus() ) {
        case 'review':       return 'label-warning'
        case 'in-progress':  return 'label-primary'
        case 'approved':     return 'label-approved'
        case 'rejected':     return 'label-danger'
        default:             return 'label-default'
      }
    })

    let statusPromise = new Promise( (resolve, reject) => {
      fetch(this.getStatusUrl(), {credentials: 'include'})
        .then(checkStatus)
        .then( response => response.json() )
        .then(data => {
          this.selectedStatus(data.status)
          this.note(data.notes)
          resolve()
        })
    })

    let mappingPromise = new Promise( (resolve, reject) => {
      fetch('/imports/api/mappings/' + window.location.search.split('=')[1], {credentials: 'include'})
        .then(checkStatus)
        .then( response => response.json() )
        .then(data => {
          this.mapping(data)
          resolve()
        })
    })

    Promise.all([statusPromise, mappingPromise])
      .then( () => this.isReady(true) )
  }

  getStatusUrl () {
    let mappingID = window.location.search.split('=')[1]
    let url = `/imports/mapping/status?id=${mappingID}`
    return url
  }

  getNotesUrl () {
    let mappingID = window.location.search.split('=')[1]
    let url = `/imports/mapping/notes?id=${mappingID}`
    return url
  }

  updateStatus () {
    fetch( this.getStatusUrl(), {
        method: 'PUT',
        credentials: 'include',
        headers: {'X-CSRF-Token': Cookies.get('csrf_token')},
        body: JSON.stringify({'status': this.selectedStatus()})
      })
      .then( checkStatus )
      .then( response => response.json() )
      .then( data => {
        this.isDanger(false)
        this.isSuccess(true)
        this.msg('Status successfully updated in the database.')
      })
      .catch( error => {
        this.isSuccess(false)
        this.isDanger(true)
        this.msg(`There was an error updating the status in the database.  ${error}`)
      })
  }

  updateNotes () {

    fetch( this.getNotesUrl(), {
        method: 'PUT',
        credentials: 'include',
        headers: {'X-CSRF-Token': Cookies.get('csrf_token')},
        body: JSON.stringify({'notes': this.note()})
      })
      .then( checkStatus )
      .then( response => response.json() )
      .then( data => {
        this.isDanger(false)
        this.isSuccess(true)
        this.msg('Your note was successfully updated in the database.')
      })
      .catch( error => {
        this.isSuccess(false)
        this.isDanger(true)
        this.msg(`There was an error updating your note in the database.  ${error}`)
      })
  }
}

ko.components.register(
  'rl-mapped',
  {viewModel: MappingView, template: template}
)
