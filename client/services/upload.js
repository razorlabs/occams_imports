import ko from 'knockout'
import pathToRegexp from 'path-to-regexp'

import checkStatus from 'utilities/fetch/checkStatus'

const ENDPOINT = pathToRegexp.compile('/imports/api/projects/:projectName/uploads')

export default class Upload {

  constructor (params) {
    this.$url = null
    this.$deleteUrl = null
    this.filename = ko.observable(null)
    this.uploadDate = ko.observable(null)

    this._update(params)
  }

  _update ({uploadDate, filename, $url, $deleteUrl}) {
    this.$url = $url
    this.$deleteUrl = $deleteUrl
    this.filename(filename)
    this.uploadDate(uploadDate)
  }

  /**
   * GET all uploads from the server
   */
  static query (params={}) {
    return fetch(
        ENDPOINT(params),
        {credentials: 'include'}
      )
      .then( checkStatus )
      .then( response => response.json() )
      .then( data => data.items.map( item => new Upload(item) ))
  }

  /**
   * POST new upload to the server
   *
   * @param uploadFile file contents to be uploaded
   */
  post (uploadFile) {

    let formData = new FormData()
    formData.append('uploadFile', uploadFile)

    return fetch(
        this.$url,
        {method: 'POST', credentials: 'include', body: formData}
      )
      .then( checkStatus )
      .then( response => response.json() )
      .then( data => this._update(data) )
  }

  /**
   * Delete selected upload
   */
  delete_ () {
    return fetch(
        this.$deleteUrl,
        {method: 'DELETE', credentials: 'include'}
      )
      .then( checkStatus )
  }
}
