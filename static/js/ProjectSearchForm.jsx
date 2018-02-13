/* Copyright 2018 Seth Michael Larson
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import axios from 'axios';
import React from "react";

export default class ProjectSearchForm extends React.Component {
    constructor (props) {
        super(props);

        this.state = {value: '', suggestions: []};

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange (event) {
        this.setState({value: event.target.value});
    }

    handleSubmit (event) {
        axios.get('/api/projects/search', {
            params: {
                name: this.state.value
            }
        }).then((response) => {
            if (response.status === 200) {
                this.setState({suggestions: response.data});
            }
        });
        event.preventDefault();
    }

    render () {
        return (
          <form>
              <input class="uk-input"
                     type="input"
                     value={this.state.value}
                     onChange={this.handleChange}/>
          </form>
        );
    }
}
