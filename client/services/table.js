import ko from 'knockout'
import pathToRegexp from 'path-to-regexp'

import checkStatus from 'utilities/fetch/checkStatus'

const ENDPOINT = pathToRegexp.compile('/imports/api/projects/:projectName/tables/:tableName?')

export default class Table {

  constructor (params) {
    this.$url = null
    this.$editUrl = null
    this.$deleteUrl = null

    this.name = ko.observable()
    this.title = ko.observable()

    this._update(params)
  }

  _update ({name, title, $url, $editUrl, $deleteUrl}) {
    this.$url = $url
    this.$editUrl = $editUrl
    this.$deleteUrl = $deleteUrl
    this.name(name)
    this.title(title)
  }

  static query (params={}) {
    return fetch(ENDPOINT(params), {credentials: 'include'})
      .then( checkStatus )
      .then( response => response.json() )
      .then( data => data.items.map( item => new Table(item) ))
  }

  post () {
    let payload = ko.toJSON(this)
    return fetch(
        ENDPOINT(),
        {method: 'POST', credentials: 'include', body: payload}
      )
      .then( checkStatus )
      .then( response => response.json() )
      .then( data => this._update(data) )
  }

  patch () {
    let payload = ko.toJSON(this)
    return fetch(
        this.$url,
        {method: 'PATCH', credentials: 'include', body: payload}
      )
      .then( checkStatus )
      .then( response => response.json() )
      .then( data => this._update(data) )
  }

  delete_ () {
    return fetch(
        this.$deleteUrl,
        {method: 'DELETE', credentials: 'include'}
      )
      .then( checkStatus )
  }


}
