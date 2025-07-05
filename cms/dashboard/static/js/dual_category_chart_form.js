class DualCategoryChartCardBlockDefinition extends window.wagtailStreamField.blocks.StructBlockDefinition {

   static SELECTORS = {
        SEGMENTS_CONTAINER: '[class="dual-category-chart-card"] [data-streamfield-list-container]',
        SEGMENT_ITEM: 'dual-category-chart-card__segments',
        SECONDARY_FIELD_VALUE: '[id$="secondary_field_value"]'
    };

    static FIELD_SUFFIXES = {
        X_AXIS: 'x_axis',
        GEOGRAPHY: 'static_fields-geography_type',
        SECONDARY_CATEGORY: 'second_category',
        PRIMARY_VALUES: 'primary_field_values',
        SECONDARY_VALUES: 'secondary_field_values',
        DATA_SCRIPT: 'subcategory-data',
        SEGMENTS: 'segments'
    };

    static DEFAULT_OPTION = {
        VALUE: '',
        TEXT: '-----'
    };

    // Category and subcategory choices
    data_script = null;
    secondary_category_choices = null;

    // Category fields (fields that drive subcategory choice options)
    x_axis_field = null;
    geography_type_field = null;
    secondary_category_field = null;

    // Subcategory fields
    primary_field_values_state = null;
    primary_field_values_inputs = null;
    secondary_field_value_state = null;
    secondary_field_value_inputs = null;

    /**
     * @name setupDataScript
     * @description Retrieve JSON data from script tag containing all category data
     * this JSON data is parsed into an object used to populate `secondary field options`.
     * @param prefix - {string} html form prefix for element IDs
     */
    setupDataScript(prefix) {
        const script_id = `${prefix}-${DualCategoryChartCardBlockDefinition.FIELD_SUFFIXES.DATA_SCRIPT}`;
        this.data_script = document.getElementById(script_id);

        if (!this.data_script) {
            console.error(`Subcategory data script not found with ID: ${script_id}`);
            this.secondary_category_choices = {};
        }

        try {
            this.secondary_category_choices = JSON.parse(this.data_script.textContent);
        } catch (error) {
            console.error('Error parsing subcategory data JSON:', error, {
                textContent: this.data_script.textContent
            });
            this.secondary_category_choices = {};
        }

    }

    /**
     * @name setupFormState
     * @description When an existing form is loaded for editing an existing page content we receive
     * the forms state in an `intialState` object. We extract the state for `primary_field_values` and
     * `secondary_field_value` so we can use them to repopulate dynamic fields.
     * @param prefix
     * @param initialState
     */
    setupFormState(prefix, initialState) {
        if (!initialState)  {
            return;
        }

        this.primary_field_values_state = initialState?.primary_field_values || [];

        this.secondary_field_value_state = initialState?.segments.map(segment => (
            segment.value?.secondary_field_value || []
        )) || [];
    }

    /**
     * @name setupCategoryFormFields
     * @description Gets all DOM elements from the dual category form that provide top level categories
     * for elements that display sub-category details. Eg: an `x_axis_field` of age will populate
     * `primary_field_values` options with age related options.
     * @param prefix - {string} html form prefix for element IDs
     */
    setupCategoryFormFields(prefix) {
        const { FIELD_SUFFIXES } = DualCategoryChartCardBlockDefinition;

        this.x_axis_field = document.getElementById(`${prefix}-${FIELD_SUFFIXES.X_AXIS}`);
        this.geography_type_field = document.getElementById(`${prefix}-${FIELD_SUFFIXES.GEOGRAPHY}`);
        this.secondary_category_field = document.getElementById(`${prefix}-${FIELD_SUFFIXES.SECONDARY_CATEGORY}`);

        const missingFields = [];
        if (!this.x_axis_field) missingFields.push(FIELD_SUFFIXES.X_AXIS);
        if (!this.geography_type_field) missingFields.push(FIELD_SUFFIXES.GEOGRAPHY);
        if (!this.secondary_category_field) missingFields.push(FIELD_SUFFIXES.SECONDARY_CATEGORY);

        if(missingFields.length > 0) {
            console.error(`Category form fields not found: ${missingFields.join(', ')}`, {
                prefix,
                x_axis_field: this.x_axis_field,
                geography_type_field: this.geography_type_field,
                secondary_category_field: this.secondary_category_field
            });
        }
    }

    /**
     * @name setupSubCategoryFormFields
     * @description Gets all DOM elements from dual category segments form that provide subcategory
     * options for a charts segments. Eg: the segments `primary_field_values` will display options related
     * to the category selected in `x_axis` field from our `primary form fields`
     * @param prefix
     */
    setupSubCategoryFormFields(prefix) {
        const { FIELD_SUFFIXES, SELECTORS } = DualCategoryChartCardBlockDefinition;

        this.primary_field_values_inputs = document.getElementById(
            `${prefix}-${FIELD_SUFFIXES.PRIMARY_VALUES}`
        );
        this.secondary_field_value_inputs = document.querySelectorAll(
            `[id^="${prefix}-${FIELD_SUFFIXES.SEGMENTS}-"]${SELECTORS.SECONDARY_FIELD_VALUE}`
        );

        const missingFields = [];
        if (!this.primary_field_values_inputs) missingFields.push(FIELD_SUFFIXES.PRIMARY_VALUES);
        if (!this.secondary_field_value_inputs) missingFields.push(FIELD_SUFFIXES.SECONDARY_VALUES);

        if (missingFields.length > 0) {
            console.error(`Sub-category form fields not found: ${missingFields.join(', ')}`, {
                prefix,
                primary_field_values: this.primary_field_values_inputs,
                secondary_field_value: this.primary_field_values_inputs?.length || 0
            });
        }
    }

    /**
     * @name initialiseFieldOptions
     * @description Populate field options on initial load based on current primary field
     * and restore saved state for existing content
     */
    initialiseFieldOptions() {
        if(!this.x_axis_field || !this.secondary_category_field || !this.secondary_category_choices) {
            return;
        }

        const { DEFAULT_OPTION } = DualCategoryChartCardBlockDefinition;

        if(this.x_axis_field && this.primary_field_values_inputs) {
            console.log('Initialising primary field values for x_axis: ', this.x_axis_field.value);
            this.updatePrimaryFieldValueOptions(this.x_axis_field.value);
        }

        if(this.secondary_category_field && this.secondary_field_value_inputs) {
            this.updateSecondaryFieldValueOptions(this.secondary_category_field.value);
        }

        if(!this.x_axis_field.value && this.primary_field_values_inputs) {
            this.primary_field_values_inputs.innerHTML = `<option value="${DEFAULT_OPTION.VALUE}">${DEFAULT_OPTION.TEXT}</option>`;
        }

        if(!this.secondary_category_field.value && this.secondary_field_value_inputs.length > 0) {
            this.secondary_field_value_inputs.forEach(input => {
                input.innerHTML = `<option value="${DEFAULT_OPTION.VALUE}">${DEFAULT_OPTION.TEXT}</option>`;
            });
        }
    }

    /**
     * @name updatePrimaryFieldValueOptions
     * @description This function rebuilds the options for instance of the `primary field values` node
     * @param subcategory_key - {string} the subcategory key used to retrieve the primary field value options.
     */
    updatePrimaryFieldValueOptions(subcategory_key) {
        const { DEFAULT_OPTION } = DualCategoryChartCardBlockDefinition;

        this.primary_field_values_inputs.innerHTML = `<option value="${DEFAULT_OPTION.VALUE}">${DEFAULT_OPTION.TEXT}</option>`;
        const options = this.secondary_category_choices[subcategory_key] || [];

        options.forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;

            if (this.primary_field_values_state && this.primary_field_values_state.includes(value)) {
                option.selected = true;
            }

            this.primary_field_values_inputs.appendChild(option);
        })
    }

    /**
     * @name updateSecondaryFieldValueOptions
     * @description This function rebuilds the options for instance of the `secondary field value` node
     * @param subcategory_key - {string} the subcategory key used to retrieve the primary field value options.
     */
    updateSecondaryFieldValueOptions(subcategory_key) {
        const { DEFAULT_OPTION } = DualCategoryChartCardBlockDefinition;

        this.secondary_field_value_inputs.forEach((secondary_field_value, index) => {
            secondary_field_value.innerHTML = `<option value="${DEFAULT_OPTION.VALUE}">${DEFAULT_OPTION.TEXT}</option>`;
            const options = this.secondary_category_choices[subcategory_key] || [];

            options.forEach(([value, label]) => {
                const option = document.createElement('option');
                option.value = value;
                option.textContent = label;

                if (this.secondary_field_value_state &&
                    this.secondary_field_value_state[index] &&
                    this.secondary_field_value_state[index].includes(value)) {
                    option.selected = true;
                }

                secondary_field_value.appendChild(option);
            });
        });
    }

    /**
     * @name storeCurrentSecondaryFieldSelections
     * @description Store the current selection state from secondary field inputs before DOM update
     */
    storeCurrentSecondaryFieldSelections() {
        if(!this.secondary_field_value_inputs) {
            return;
        }

        const { DEFAULT_OPTION } = DualCategoryChartCardBlockDefinition;

        this.secondary_field_value_state = Array.from(this.secondary_field_value_inputs).map(input => {
            const selectedValues = [];

            for (let i = 0; i < input.options.length; i++) {
                const option = input.options[i];
                if (option.selected && option.value !== DEFAULT_OPTION.VALUE) {
                    selectedValues.push(option.value);
                }
            }

            return selectedValues;
        });
    }

    /**
     * @name observeSegmentsBlocks
     * @description This makes use of the `MutationObserver` API to watch for new `segment` `ListBlock` items
     * added to the DOM, when this is `observed` a number of functions are called that update the list of
     * `SecondaryFormFields` and then update the options of these lists to ensure they align with the primary fields.
     * @param prefix
     */
    observeSegmentBlocks(prefix) {
        const { SELECTORS } =  DualCategoryChartCardBlockDefinition;
        const segments_container = document.querySelector(SELECTORS.SEGMENTS_CONTAINER)

        if(!segments_container) {
            console.warn("Segments container not found - observer disabled");
            return;
        }

        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1 && node.classList.contains(SELECTORS.SEGMENT_ITEM)) {

                            this.storeCurrentSecondaryFieldSelections();
                            this.setupSubCategoryFormFields(prefix);
                            if (this.secondary_category_field.value) {
                                this.updateSecondaryFieldValueOptions(this.secondary_category_field.value);
                            }

                        }
                    })
                }
            })
        })

        observer.observe(segments_container, {
            childList: true,
            attributes: true,
            subtree: true
        })
    }

    /**
     * @name setupEvents
     * @description Setup event handlers for dynamic choice fields `secondary_category` and `x_axis_field`.
     */
    setupEvents() {
        if(!this.x_axis_field || !this.secondary_category_field) {
           console.warn("x-axis or secondary category field(s) not found");
           return;
        }

        this.x_axis_field.addEventListener('change', (evt) => {
            this.primary_field_values_state = [];
            this.updatePrimaryFieldValueOptions(evt.target.value)
        });

        this.secondary_category_field.addEventListener('change', (evt) => {
            this.secondary_field_value_state = [];
            this.updateSecondaryFieldValueOptions(evt.target.value);
        });
    }

    render(placeholder, prefix, initialState, initialError) {
        const block = super.render(placeholder, prefix, initialState, initialError);

        // setup form data
        this.setupDataScript(prefix);
        this.setupFormState(prefix, initialState);

        // setup primary and secondary form fields
        this.setupCategoryFormFields(prefix);
        this.setupSubCategoryFormFields(prefix);

        // Initial population of field options based on current/initial values
        this.initialiseFieldOptions();

        // Setup observer for watching segments list and event handlers on
        this.observeSegmentBlocks(prefix);
        this.setupEvents();

        return block;
    }

}

window.telepath.register(
    'cms.dynamic_content.dynamic_cards.DualCategoryChartCard',
    DualCategoryChartCardBlockDefinition,
);
