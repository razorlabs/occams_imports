import ResponseError from './ResponseError'

/**
 * Checks the status of the response and throws an eror if not 2XX
 *
 * @param {object} response - The returned response from the "fetch" promise
 * @throws {FetchResponseError} When response is not acceptable
 * @return {Promise} The original response promise
 */
export default function checkStatus (response) {
  if ( response.status >= 200 && response.status < 300 ) {
    return response
  } else {
    throw new ResponseError(response)
  }
}
