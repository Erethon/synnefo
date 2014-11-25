import DS from 'ember-data';
import Ember from 'ember';

export default DS.RESTAdapter.extend({
  headers: function(){
    return {'X-Auth-Token': this.get('settings').get('token'),
              'X-Requested-With': 'XMLHttpRequest',
              'Content-Type': 'application/json'};
  }.property(),

  host: function(){
    return this.get('settings').get('storage_host');
  }.property(),

  user_catalogs_url: function(){
    return this.get('settings').get('account_url')+ '/user_catalogs/';
  }.property(),

  buildURL: function(type, id, record){
    var url = [],
        host = this.get('host');
    url.push(host);
    if (id) {
      url.push(id);
    }
    url = url.join('/');
    return url;
  },

  ajaxSuccess: function(jqXHR, jsonPayload) {

    // get all headers as a string
    var headers = jqXHR.getAllResponseHeaders();

    // put all headers that start with X-Account-Group in an array
    var group_headers_arr = headers.match(/\bX-Account-Group-\w[^\b]*?\b/g);

    var groups = [];

    if (group_headers_arr) {
      group_headers_arr.forEach(function(h){
        var obj = {};
        obj.id = h.replace('X-Account-Group-', '');
        obj.name = h.replace('X-Account-Group-', '');
        obj.uuids = jqXHR.getResponseHeader(h);
        groups.push(obj);
      });
    }

    jsonPayload.groups = groups;
    return jsonPayload;
  },

  createRecord: function(store, type, record) {

    var url = this.buildURL(type.typeKey)+'?update=';
    var user_catalogs_url = this.get('user_catalogs_url');
    var headers = this.get('headers');

    var header = 'X-Account-Group-'+record.get('name');

    this.user_catalogs(null, record.get('emails')).then(function(data){
      var uuids_arr = [];
      data.forEach(function(u){
        uuids_arr.push(u.uuid);
      });
      var uuids = uuids_arr.join(',');

      headers[header] = uuids;

      return new Ember.RSVP.Promise(function(resolve, reject) {
        jQuery.ajax({
          type: 'POST',
          url: url,
          dataType: 'text',
          headers: headers,
        }).then(function(data) {
          Ember.run(null, resolve, data);
        }, function(jqXHR) {
          var response = Ember.$.parseJSON(jqXHR.responseText);
          jqXHR.then = null; // tame jQuery's ill mannered promises
          Ember.run(null, reject, jqXHR);
        });
    
      });
    });
    return false;
  },

  deleteRecord: function(store, type, record){
    var url = this.buildURL(type.typeKey)+'?update=';
    var headers = this.get('headers');

    var header = 'X-Account-Group-'+record.get('name');
    headers[header] = '~';

    return new Ember.RSVP.Promise(function(resolve, reject) {

      jQuery.ajax({
        type: 'POST',
        url: url,
        dataType: 'text',
        headers: headers,
      }).then(function(data) {
        Ember.run(null, resolve, data);
      }, function(jqXHR) {
        jqXHR.then = null; // tame jQuery's ill mannered promises
        Ember.run(null, reject, jqXHR);
      });
    });

  },

  user_catalogs: function(uuids, emails) {

    var user_catalogs_url = this.get('user_catalogs_url');
    var headers = this.get('headers');

    var uuids_arr = [];
    var displaynames_arr = [];

    if (uuids)  {
      uuids.split(',').forEach(function(u){
        uuids_arr.push(u.trim());
      });
    }

    if (emails) {
      emails.split(',').forEach(function(u){
        displaynames_arr.push(u.trim());
      });
    }

    var data = JSON.stringify({"uuids": uuids_arr, "displaynames": displaynames_arr});


    return new Ember.RSVP.Promise(function(resolve, reject) {

      jQuery.ajax({
        type: 'POST',
        url: user_catalogs_url,
        headers: headers,
        data: data
      }).then(function(data) {

        var res = [];
        
        if (Object.keys(data.uuid_catalog).length>0){
          var users = data.uuid_catalog;
          for (var key in users) {
            if (users.hasOwnProperty(key)) {
              res.push({email: users[key], uuid: key});
            }
          }
        }

        if (Object.keys(data.displayname_catalog).length>0){
          var users = data.displayname_catalog;
          for (var key in users) {
            if (users.hasOwnProperty(key)) {
              res.push({uuid: users[key], email: key});
            }
          }
        }

        Ember.run(null, resolve, res);
      }, function(jqXHR) {
        jqXHR.then = null; // tame jQuery's ill mannered promises
        Ember.run(null, reject, jqXHR);
      });
    });
 
  },

});
