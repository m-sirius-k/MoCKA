window.injectToAIField = function(text) {
    const targets = [
        { name: 'ChatGPT', selector: '#prompt-textarea' },
        { name: 'Claude', selector: 'div[contenteditable="true"]' },
        { name: 'Gemini', selector: 'div.rich-textarea [contenteditable=\"true\"], textarea' },
        { name: 'Perplexity', selector: 'textarea' }
    ];

    let element = null;
    for (const target of targets) {
        element = document.querySelector(target.selector);
        if (element) break;
    }

    if (!element) return;

    element.focus();
    if (element.tagName === 'TEXTAREA' || element.tagName === 'INPUT') {
        element.value = text;
    } else {
        element.innerText = text;
    }

    ['input', 'change', 'blur'].forEach(type => {
        element.dispatchEvent(new Event(type, { bubbles: true }));
    });

    element.style.outline = '3px solid #00ff7f';
    setTimeout(() => { element.style.outline = 'none'; }, 1000);
};
