import ko from 'knockout'
import pathToRegexp from 'path-to-regexp'
import Cookies from 'js-cookie'

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
   * @param schema name of the schema associated with the upload
   */
  post (uploadFile, schema) {
    let csrf_token = Cookies.get('csrf_token')
    let headers = new Headers()
    headers.append('X-CSRF-Token', csrf_token)

    let formData = new FormData()
    formData.append('uploadFile', uploadFile)
    formData.append('schema', schema)

    return fetch(
        this.$url,
        {
          method: 'POST',
          credentials: 'include',
          body: formData,
          headers: headers
        }
      )
      .then( checkStatus )
      .then( response => response.json() )
      .then( data => this._update(data) )
  }

  /**
   * Delete selected upload
   */
  delete_ () {
    let csrf_token = Cookies.get('csrf_token')
    let headers = new Headers()
    headers.append('X-CSRF-Token', csrf_token)

    return fetch(
        this.$deleteUrl,
        {method: 'DELETE', credentials: 'include', headers: headers}
      )
      .then( checkStatus )
  }
}
