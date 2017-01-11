import checkStatus from './checkStatus'
import ResponseError from './ResponseError'

describe('#checkStatus', () => {

  it('should return the response on status 2XX', () => {
    console.log(checkStatus)
    let response = new Response(new Blob(), {status: 200})
    checkStatus(response).should.have.property('status', 200)
  })

  it('should throw an error if the response is not in the 2xx range', () => {
    let response = new Response(new Blob(), {status: 500}),
        call = () => checkStatus(response)
    // Just check for generic Error because PhantomJS won't handle it
    call.should.throw(Error)
  })

})

