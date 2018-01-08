const chakram = require('chakram')
const util = require('util')
const faker = require('faker')
const config = require('../config')
const tools = require('../test_utils')
const generator = require('../generator')
const expect = chakram.expect

describe('users/profiles/', () => {
  const profile_uri = tools.get_request_uri('users/profiles/')
  const user_schema = tools.get_schema('users', 'profiles/')

  beforeEach(() => {
    this.new_user = generator.user()
  })

  it('GET all user profiles should return a list of profiles', async () => {
    const response = await chakram.get(profile_uri)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(user_schema)
  })

  it('DELETE deleting a new user should remove the user', async () => {
    const response = await chakram.post(profile_uri, this.new_user)
    let expect_json = JSON.parse(JSON.stringify(this.new_user))
    delete expect_json.password
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(expect_json)
    const user_uri = profile_uri + response.body.id + '/'

    const del_response = await chakram.delete(user_uri, {})
    expect(del_response).to.have.status(204)

    const get_response = await chakram.get(user_uri)
    expect(get_response).to.have.status(404)
  })

  it('PATCH changing a users email should update the email', async () => {
    let modified_user = JSON.parse(JSON.stringify(this.new_user))
    modified_user.profile.bio = faker.lorem.sentence()
    delete modified_user.username
    delete modified_user.password
    const response = await chakram.post(profile_uri, this.new_user)
    expect(response).to.have.status(201)
    const user_uri = profile_uri + response.body.id + '/'

    const patch_response = await chakram.patch(user_uri, modified_user)
    expect(patch_response).to.have.status(200)

    const get_response = await chakram.get(user_uri)
    expect(get_response).comprise.of.json(modified_user)
  })
})

describe('users/{user_id}/emails/', async () => {
  let me, email_uri
  before(async () => {
    const me_uri = tools.get_request_uri('me/')

    const response = await chakram.get(me_uri)
    expect(response).to.have.status(200)
    me = response.body
    email_uri = tools.get_request_uri(util.format('users/%s/emails/', me.id))
  })

  beforeEach(() => {
    this.email = generator.email()
  })

  afterEach(async () => {
    if (this.delete_email) {
      const response = await chakram.delete(email_uri + this.delete_email + '/', {})
      expect(response).to.have.status(204)
      this.delete_email = undefined
    }
  })

  it('POST a user email should return the email', async () => {
    const response = await chakram.post(email_uri, this.email)
    expect(response).to.have.status(201)
    this.delete_email = response.body.id

    const get_response = await chakram.get(email_uri + response.body.id + '/')
    expect(get_response).to.have.status(200)
    expect(get_response).comprise.of.json(this.email)
  })

  it('PUT changing the address should return the new address', async () => {
    let modified_email = JSON.parse(JSON.stringify(this.email))
    modified_email.address = faker.internet.exampleEmail()
    const response = await chakram.post(email_uri, this.email)
    expect(response).to.have.status(201)
    expect(response).comprise.of.json(this.email)
    this.delete_email = response.body.id
    const uri = email_uri + response.body.id + '/'

    const put_response = await chakram.put(uri, modified_email)
    expect(put_response).to.have.status(200)
    expect(put_response).comprise.of.json(modified_email)
  })

  it('PATCH changing the address should return the new address', async () => {
    let modified_email = JSON.parse(JSON.stringify(this.email))
    modified_email.address = faker.internet.exampleEmail()
    const response = await chakram.post(email_uri, this.email)
    expect(response).to.have.status(201)
    expect(response).comprise.of.json(this.email)
    this.delete_email = response.body.id
    const uri = email_uri + response.body.id + '/'

    const put_response = await chakram.patch(uri, modified_email)
    expect(put_response).to.have.status(200)
    expect(put_response).comprise.of.json(modified_email)
  })

  it('DELETE deleting the email should remove the email', async () => {
    const response = await chakram.post(email_uri, this.email)
    expect(response).to.have.status(201)
    expect(response).comprise.of.json(this.email)

    const del_response = await chakram.delete(email_uri + response.body.id + '/', {})
    expect(del_response).to.have.status(204)
  })
})

describe('users/{user_id}/api-key/', () => {
  let schema = tools.get_schema('users', 'api-key/')
  let api_key_uri
  before(async () => {
    const me_uri = tools.get_request_uri('me/')
    const response = await chakram.get(me_uri)
    expect(response).to.have.status(200)
    me = response.body
    api_key_uri = tools.get_request_uri(util.format('users/%s/api-key/', me.id))
  })

  it('GET user api key should retrieve a valid api key', async () => {
    const response = await chakram.get(api_key_uri)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(schema)
  })
})

describe('users/{user_id}/ssh-key/', () => {
  let ssh_key_uri
  const ssh_schema = tools.get_schema('users', 'ssh-key/')
  before(async () => {
    const me_uri = tools.get_request_uri('me/')
    const response = await chakram.get(me_uri)
    expect(response).to.have.status(200)
    me = response.body
    ssh_key_uri = tools.get_request_uri(util.format('users/%s/ssh-key/', me.id))
  })

  it('GET my ssh key should provide a valid ssh key', async () => {
    const response = await chakram.get(ssh_key_uri)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(ssh_schema)
  })
})
