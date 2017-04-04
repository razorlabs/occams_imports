import ko from 'knockout'
import Cookies from 'js-cookie'
import {Mapping} from 'services'
import checkStatus from 'utilities/fetch/checkStatus'
import 'components/choice-widget'
import 'components/variable-widget'
import template from './index.html'


function getUrlParams(search) {
  let hashes = search.slice(search.indexOf('?') + 1).split('&')
  let params = {}
  hashes.map(hash => {
    let [key, val] = hash.split('=')
    params[key] = decodeURIComponent(val)
  })
  return params
}


class MappingView {

  constructor () {
    this.isReady = ko.observable(false)
    this.isLoading = ko.observable(false)

    this.mapping = ko.observable()

    this.loadMapping()
  }

  loadMapping () {
    let params = getUrlParams(window.location.search)

    if (!params.id){
      this.mapping(new Mapping())
      this.isReady(true)
      return
    }

    fetch('/imports/mappings/view_mapped?id=' + params.id, {
        credentials: 'include',
        // Use the old calling style as the API has not been updated yet
        headers: new Headers({'X-Requested-With': 'XMLHttpRequest'})
      })
      .then( checkStatus )
      .then( response => response.json() )
      .then( data => {
        this.mapping(new Mapping(data))
        this.isReady(true)
      })
  }

  saveMapping () {
    let payload = ko.toJSON(this.mapping)

    this.isLoading(true)

    fetch('/imports/mappings/imputation', {
        method: 'POST',
        headers: new Headers({
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRF-Token': Cookies.get('csrf_token')
        }),
        credentials: 'include',
        body: payload
      })
      .then( checkStatus )
      .then( response => {
        console.log(response)
        return response
      })
      .then( response => response.json() )
      .then( data => window.location.href = data.__next__ )
  }

}

ko.components.register('rl-impute-map', {
  viewModel: MappingView,
  template: template
})
