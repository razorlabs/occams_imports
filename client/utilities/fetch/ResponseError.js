import ExtendableError from 'utilities/ExtendableError'

/**
 * Error thrown when fetch status fails
 * @class
 */
export default class ResponseError extends ExtendableError{

  constructor(response) {
    super(response.statusText)

    this.name = this.constructor.name
    this.message = message

    /**
     * The original reponse that caused the error
     * @public
     */
    this.response = response

  }

}
