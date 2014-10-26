import Ember from 'ember';

import ObjectController from '../object';

export default ObjectController.extend({
  needs: ['objects'],

  versions: function(){
    var timestamp = new Date().getTime();
    this.store.set('object_name', this.get('model').get('name'));
    return this.store.find('version', {format:'json', version:'list', t: timestamp});
  }.property('model'),

});