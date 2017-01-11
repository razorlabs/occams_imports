/**
 * HTTP utilities
 */

/**
 * Checks the status of the response and throws an exception if unparseable
 *
 * This method assumes that anything above a 400 is considered to be
 * unparseable and thus should be wrapped in an exception that can be catch
 * at a later promise-handler. If the response is a 400, it is considered
 * to be a validation error from the server that can still be parsed for
 * details.
 *
 * @param {object} response - The returned response from the "fetch" promise
 * @return {Promise} The parsed JSON response
 */
export function checkStatus (response) {
  if ( response.status > 400 ) {
    let error = new Error(response.statusText)
    error.response = response
    throw error
  } else {
    return response.json()
  }
}
