const chakram = require('chakram');
const util = require('util');
const config = require('./config');
const tools = require('./test_utils');
const faker = require('faker');
const expect = chakram.expect;

const namespace = config.username;

before(() => {
    let token = tools.login(config.username, config.password);
    this.options = {
        headers: {
            Authorization: util.format('%s %s', 'Bearer', token)
        }
    }
});

describe('{namespace}/search/', () => {
    let search_uri = tools.get_request_uri(util.format('%s/search/', namespace));
});
