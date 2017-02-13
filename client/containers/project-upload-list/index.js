import ko from 'knockout'
import pathToRegexp from 'path-to-regexp'

import {Upload} from 'services'
import template from './index.html'


export default class ProjectUploadListView{

  /**
   * Create a project detail view
   */
  constructor(params) {

    this.project = params.project
    this.showUploadModal = ko.observable(false)
    this.isReady = ko.observable(false)
    this.uploads = ko.observableArray([])
    this.hasUploads = ko.pureComputed(() => this.uploads().length > 0)

    this.selectedUploads = ko.observableArray([]);

    this.modalHeaderName = ko.computed(() => {
      return this.project.title() + ' file upload.'
    })

    this.atLeastOneChecked = ko.computed(() => {
      return this.selectedUploads().length > 0
    })

    Upload.query({projectName: this.project.name()})
      .then( uploads => {
        this.uploads(uploads)
        this.sortUploadsByName()
        this.isReady(true)
      })
  }

  /**
   * Sort the current listing of uploads in place by name
   */
  sortUploadsByName () {
    this.uploads.sort((a, b) => a.filename().localeCompare(b.filename()))
  }

  /**
   * Clears all UI settings
   */
  clear () {
    this.showUploadModal(false)
  }

  removeUploads () {
    ko.utils.arrayForEach(this.selectedUploads(), (upload) => {
      upload.delete_()
      this.uploads.remove(upload)
      this.selectedUploads.remove(upload)
    })
  }


  /**
   * Create a new upload
   */
  beginUpload() {

    let endpoint = pathToRegexp.compile('/imports/api/projects/:projectName/uploads')

    this.showUploadModal(true)
    this.newUpload = new Upload({'$url': endpoint(
        {'projectName':this.project.name()})})
  }

  /**
   * Get the file contents and POST
   */
  uploadFile(upload) {
    this.showUploadModal(false)

    let uploadFile = upload['data-file'].files[0]

    this.newUpload.post(uploadFile)
    this.uploads.push(this.newUpload)
  }

  applyMappings(){
    let url = '/imports/api/projects/' + this.project.name() + '/apply'
    fetch(
            url,
            {
              method: 'GET',
              credentials: 'include'
            }
          )
  }
}

ko.components.register(
  'rl-project-upload-list',
  {
    template: template,
    viewModel: ProjectUploadListView
  }
)