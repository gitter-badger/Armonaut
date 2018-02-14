import Backbone from 'backbone';


export default class Project extends Backbone.Model {
    initialize (attributes) {
        this.owner = attributes.owner;
        this.name = attributes.name;

        this.url = '/api/projects/' + this.owner + '/' + this.name;

        this.on('changed:owner', this.updateUrl);
        this.on('changed:name', this.updateUrl);
    }

    updateUrl () {
        this.url = '/api/projects/' + this.owner + '/' + this.name;
    }
}