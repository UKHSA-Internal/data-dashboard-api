console.log("metric_dropdown_manager loaded");

class BaseMetricsElementBlockDefinition extends globalThis.wagtailStreamField.blocks.StructBlockDefinition {
    async render(placeholder, prefix, initialState, initialError) {
        console.log("initialState", initialState);
        const block = super.render(
            placeholder,
            prefix,
            initialState,
            initialError,
        );

        const metricForm = new MetricForm(initialState);
        await metricForm.render(block);
        console.log(
            "topic value before submit",
            this.topicField.value,
        );

        console.log(
            "metric value before submit",
            this.metricField.value,
        );
        return block;
    }
}

class MetricForm {
    constructor(initialState) {
        this.initialState = initialState;
    }
    topicField = null;
    metricField = null;
    isPublicField = null;

    setupFields(rootNode) {
        this.topicField = rootNode.querySelector(
            'select[name$="topic"]',
        );

        this.metricField = rootNode.querySelector(
            'select[name$="metric"]',
        );

        this.isPublicField = document.querySelector(
            'input[name="is_public"]',
        );

        if (!this.topicField) {
            console.error("Topic field not found");
        }

        if (!this.metricField) {
            console.error("Metric field not found");
        }
        this.savedMetricValue = this.metricField?.value;
        this.savedTopicValue = this.topicField?.value;
        const savedTopic = this.initialState?.topic?.[0];
    
        if (savedTopic) {
            const matchingOption = [...this.topicField.options].find(
                option =>
                    option.text === savedTopic ||
                    option.value === savedTopic,
            );
    
            if (matchingOption) {
                this.topicField.value = matchingOption.value;
            }
        }

        const savedMetric = this.initialState?.metric?.[0];

        const matchingChoice = choices.find(
            ([id, name]) => name === savedMetric
        );

        if (matchingChoice) {
            this.metricField.value = matchingChoice[0];
        }
    }


    clearMetricDropdown(message = "Select topic first") {
        this.metricField.innerHTML = "";

        const option = document.createElement("option");
        option.value = "";
        option.textContent = message;

        this.metricField.appendChild(option);
    }

    populateMetricDropdown(choices) {
        console.log("savedMetric", this.initialState?.metric?.[0]);
        console.log("current metric value", this.metricField.value);
        console.log("choices", choices);
        const savedMetric = this.initialState?.metric?.[0];

        this.metricField.innerHTML = "";

        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = "--------";
        this.metricField.appendChild(defaultOption);

        choices.forEach(([value, label]) => {
            const option = document.createElement("option");

            option.value = value;
            option.textContent = label;

            if (
                value === savedMetric ||
                label === savedMetric
            ) {
                option.selected = true;
            }

            this.metricField.appendChild(option);
        });
    }

    async fetchChoices(endpoint, dataItemId, queryParams = {}) {
        try {
            const queryString =
                typeof queryParams.is_public === "boolean"
                    ? `?is_public=${queryParams.is_public}`
                    : ""

            const url = `/api/data-hierarchy/${endpoint}/${dataItemId}${queryString}`
            const response = await fetch(url)

            if (!response.ok) {
                console.error(`Failed to fetch ${endpoint}`);
                return [];
            }

            const data = await response.json();

            return data.choices || [];
        } catch (error) {
            console.error(`Error fetching ${endpoint}:`, error);
            return [];
        }
    }

    async loadMetrics() {
        console.log(
            "topic options",
            [...this.topicField.options].map(option => ({
                value: option.value,
                text: option.text,
                selected: option.selected,
            })),
        );
        let topicValue = this.topicField?.value;
        console.log("topicValue before", topicValue);

        
        if (!topicValue) {
            this.clearMetricDropdown("Select topic first");
            return;
        }
        // convert topic name to id here?

        if (topicValue && Number.isNaN(Number(topicValue))) {
            const matchingIdOption = [...this.topicField.options].find(
                option =>
                    option.text === topicValue &&
                    !Number.isNaN(Number(option.value)),
            );

            if (matchingIdOption) {
                topicValue = matchingIdOption.value;
            }
        }

        console.log("topicValue after conversion", topicValue);
        
        const choices = await this.fetchChoices(
            "metrics",
            topicValue,
            {
                is_public: this.isPublicField?.checked,
            },
        );

        if (choices.length > 0) {
            this.populateMetricDropdown(choices);
        } else {
            this.clearMetricDropdown("No metrics available");
        }
    }

    setupEvents() {
        this.topicField?.addEventListener(
            "change",
            () => this.loadMetrics(),
        );

        this.isPublicField?.addEventListener(
            "change",
            () => this.loadMetrics(),
        );
    }

    async render(block) {
        const rootNode = block.container[0];

        this.setupFields(rootNode);

        const savedTopic = this.topicField.value;

        if (
            savedTopic &&
            Number.isNaN(Number(savedTopic))
        ) {
            const matchingOption = [...this.topicField.options].find(
                option => option.text === savedTopic,
            );

            if (matchingOption) {
                this.topicField.value = matchingOption.value;
            }
        }

        await this.loadMetrics();
        this.setupEvents();
    }

}

globalThis.telepath.register(
    "cms.dynamic_content.elements.BaseMetricsElement",
    BaseMetricsElementBlockDefinition,
);