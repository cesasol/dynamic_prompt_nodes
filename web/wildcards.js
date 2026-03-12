import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";

const NODE_NAMES = new Set([
    "DynamicPromptRandom",
    "DynamicPromptCombinatorial",
    "DynamicPromptCyclical",
]);

const SENTINEL = "── insert wildcard ──";

let wildcardCache = null;

async function loadWildcards() {
    if (wildcardCache !== null) return wildcardCache;
    try {
        const resp = await api.fetchApi("/dynamic_prompts/wildcards");
        wildcardCache = await resp.json();
    } catch (e) {
        console.error("[DynamicPrompts] Failed to fetch wildcard list:", e);
        wildcardCache = [];
    }
    return wildcardCache;
}

app.registerExtension({
    name: "DynamicPrompts.WildcardDropdown",

    async nodeCreated(node) {
        if (!NODE_NAMES.has(node.comfyClass)) return;

        const names = await loadWildcards();
        if (names.length === 0) return;

        const templateWidget = node.widgets?.find(w => w.name === "template");
        if (!templateWidget) return;

        const widget = node.addWidget(
            "combo",
            "wildcard_insert",
            SENTINEL,
            (value) => {
                if (value === SENTINEL) return;
                const cur = templateWidget.value ?? "";
                templateWidget.value = cur ? `${cur}, __${value}__` : `__${value}__`;
                requestAnimationFrame(() => {
                    widget.value = SENTINEL;
                });
            },
            { values: [SENTINEL, ...names], serialize: false }
        );
    },
});
