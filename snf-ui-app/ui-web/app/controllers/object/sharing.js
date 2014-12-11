import Ember from 'ember';

import ObjectController from '../object';

export default ObjectController.extend({
  isPublic: function(){
    return this.get('model').get('public_link')? true : false;
  }.property('model.public_link'),

  isShared: function(){
    return this.get('model').get('sharing')? true: false;
  }.property('model.sharing'),

  watchPublic: function(){
    this.send('togglePublic');
  }.observes('isPublic'),

  actions: {
    togglePublic: function(){
      var object = this.get('model');
      this.store.setPublic(object, this.get('isPublic')).then(function(data){
        object.set('public_link', data);
      });
    },
    changePermissions: function(){
      console.log('Will change permissions');
    }
  }
});
