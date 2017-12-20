const chakram = require('chakram')
const util = require('util')
const config = require('./config')
const tools = require('./test_utils')
const faker = require('faker')
const expect = chakram.expect

const namespace = config.username

before(async () => {
  const token = await tools.login(config.username, config.password)
  this.options = {
    headers: {
      Authorization: util.format('%s %s', 'Bearer', token),
    },
  }
})

describe('{namespace}/search/', () => {
  const search_uri = tools.get_request_uri(util.format('%s/search/', namespace))
  const schema = {
    type: 'object',
    properties: {
      servers: {
        type: 'object',
        properties: {
          results: {
            type: 'array',
          },
        },
      },
      users: {
        type: 'object',
        properties: {
          results: {
            type: 'array',
          },
        },
      },
    },
  }

  it('GET search for admin should return admin', async () => {
    const query = '?q=admin'
    const response = await chakram.get(search_uri + query, this.options)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(schema)
    expect(response.body.users.results[0].username).to.equal('admin')
  })
})
