import ko from 'knockout'
import pathToRegexp from 'path-to-regexp'

import 'bindings/select2'

import {Schema, Upload} from 'services'
import template from './index.html'


export default class ProjectUploadListView{

  /**
   * Create a project detail view
   */
  constructor(params) {

    this.isTarget = false
    this.schema = ko.observable('')

    this.project = params.project
    this.showUploadModal = ko.observable(false)
    this.isReady = ko.observable(false)
    this.uploads = ko.observableArray([])
    this.hasUploads = ko.pureComputed(() => this.uploads().length > 0)

    this.selectedUploads = ko.observableArray([])
    this.addMoreUploads = ko.observable(false)

    this.nextSchemaSearch = () => this.schema() && this.schema().name()
    this.querySchemaData = term => {
      return {
        vocabulary: 'available_schemata',
        is_target: this.isTarget,
        term: term
      }
    }

    this.parseSchemaResults = data => {
      return {
        results: data.schemata.map( value => new Schema(value) )
      }
    }

    this.atLeastOneChecked = ko.computed(() => this.selectedUploads().length > 0)

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
    this.addMoreUploads(false)
    this.showUploadModal(false)
  }

  removeUploads () {
    this.selectedUploads().forEach( upload => {
      upload.delete_()
      .then(this.uploads.remove(upload))
    })
    this.selectedUploads([])
  }

  /**
   * Create a new upload
   */
  beginUpload() {

    let endpoint = pathToRegexp.compile('/imports/api/projects/:projectName/uploads')

    this.showUploadModal(true)
    this.schema('')
    this.newUpload = new Upload({'$url': endpoint(
        {'projectName':this.project.name()})})
  }

  /**
   * Get the file contents and POST
   */
  uploadFile(upload) {

    let uploadFile = upload['data-file'].files[0]
    let schema = upload['schema'].value

    this.newUpload.post(uploadFile, schema)
      .then(() => {
        this.uploads.push(this.newUpload)

        if (this.addMoreUploads()) {
          upload.reset()
          upload['add_another'].checked = true
          this.beginUpload()
        } else {
          this.clear()
        }
      })
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
