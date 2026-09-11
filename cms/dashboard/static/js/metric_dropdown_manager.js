class BaseMetricsElementBlockDefinition extends globalThis.wagtailStreamField.blocks.StructBlockDefinition {
    render(placeholder, prefix, initialState, initialError) {
        const block = super.render(
            placeholder,
            prefix,
            initialState,
            initialError,
        );

        const metricForm = new MetricForm();
        metricForm.render(block);
        return block;
    }
}

class MetricForm {
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
    }

    clearMetricDropdown(message = "Select topic first") {
        this.metricField.innerHTML = "";

        const option = document.createElement("option");
        option.value = "";
        option.textContent = message;

        this.metricField.appendChild(option);
    }

    populateMetricDropdown(choices) {
        const currentValue = this.metricField.value;

        this.metricField.innerHTML = "";

        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = "* All metrics";

        this.metricField.appendChild(defaultOption);

        choices.forEach(([value, label]) => {
            const option = document.createElement("option");

            option.value = value;
            option.textContent = label;

            if (value === currentValue) {
                option.selected = true;
            }

            this.metricField.appendChild(option);
        });
    }

    async fetchChoices(endpoint, dataItemId, queryParams = {}) {
        try {
            let url = `/api/data-hierarchy/${endpoint}/${dataItemId}`;

            if ("is_public" in queryParams) {
                url += `?is_public=${queryParams.is_public}`;
            }

            const response = await fetch(url);

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
        const topicValue = this.topicField?.value;

        if (!topicValue) {
            this.clearMetricDropdown("Select topic first");
            return;
        }

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

    render(block) {
        const rootNode = block.container[0];

        this.setupFields(rootNode);

        if (!this.topicField || !this.metricField) {
            return;
        }

        this.loadMetrics();

        this.setupEvents();
    }
}

globalThis.telepath.register(
    "cms.dynamic_content.elements.BaseMetricsElement",
    BaseMetricsElementBlockDefinition,
);