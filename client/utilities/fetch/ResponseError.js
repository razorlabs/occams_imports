import ExtendableError from 'utilities/ExtendableError'

/**
 * Error thrown when fetch status fails
 * @class
 */
export default class ResponseError extends ExtendableError{

  constructor(response) {
    super(response.statusText)

    /**
     * The original reponse that caused the error
     * @public
     */
    this.response = response

  }

}
