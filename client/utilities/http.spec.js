
import {checkStatus} from './http'

describe('http', () => {

  describe('#checkStatus', function() {

    it('should return a JSON document on successful response', () => {
      let apiData = {mydata: 420},
          blob = new Blob([JSON.stringify(apiData)], {type : 'application/json'}),
          response = new Response(blob, {status: 200})
      return checkStatus(response).then( data => data.should.eql(apiData) )
    })

    it('should interpret error code 400 to be validation errors', () => {
      let apiData = {myfield: ['This field is required']},
          blob = new Blob([JSON.stringify(apiData)], {type : 'application/json'}),
          response = new Response(blob, {status: 400})
      return checkStatus(response).then( data => data.should.eql(apiData) )
    })

    it('should throw an error if the response is greather than 400', () => {
      let call = () => checkStatus( new Response(new Blob(), {status: 500}) )
      call.should.throw(Error)
    })

  })

})
