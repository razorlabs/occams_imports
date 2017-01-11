import ko from 'knockout'
import pathToRegexp from 'path-to-regexp'

import {checkStatus} from 'utilities/http'

const ENDPOINT = pathToRegexp.compile('/imports/api/projects/:projectName?')

export default class Project {

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
    return fetch(
        ENDPOINT(params),
        {credentials: 'include'}
      )
      .then( checkStatus )
      .then( data => data.items.map( item => new Project(item) ))
  }

  post () {
    let payload = ko.toJSON(this)
    return fetch(
        ENDPOINT(),
        {method: 'POST', credentials: 'include', body: payload}
      )
      .then( checkStatus )
      .then( data => this._update(data) )
  }

  patch () {
    let payload = ko.toJSON(this)
    return fetch(
        this.$url,
        {method: 'PATCH', credentials: 'include', body: payload}
      )
      .then( checkStatus )
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
