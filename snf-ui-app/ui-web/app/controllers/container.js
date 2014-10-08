import Ember from 'ember';

export default Ember.ObjectController.extend({
  title: 'object controller title',

  availableProjects: function(){
    var that = this;
    return this.store.filter('project',{mode:"member"}, function(p) {
      return (p.get('id') !== that.get('selectedProject').get('id')) && ( that.get('model').get('bytes')< p.get('diskspace'));
    });
  }.property('selectedProject'),

  selectedProject: function(){
    return this.get('model').get('project');
  }.property('project'),

  watchProject: function(){
    this.send('reassignContainer');
  }.observes('selectedProject'),

  actions: {
    deleteContainer: function(){
      var container = this.get('model');
      container.deleteRecord();
      container.save();
    },
    emptyContainer: function(){
      var container = this.get('model');
      this.store.emptyContainer();
    },
    reassignContainer: function(){
      var container = this.get('model');
      this.store.reassignContainer();
    }
  }

});
