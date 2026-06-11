/******/ (() => { // webpackBootstrap
var IframeSessionScript = /** @class */ (function () {
    function IframeSessionScript() {
        window.addEventListener('requestExtensionToken', function (event) {
            var port = chrome.runtime.connect({ name: 'request_token' });
            port.onMessage.addListener(function (msg) {
                window.dispatchEvent(new CustomEvent('extensionTokenResponse', {
                    detail: { token: msg.token, requestId: '123' }
                }));
                port.disconnect();
            });
        });
    }
    return IframeSessionScript;
}());
var iframeSessionScript = new IframeSessionScript();

/******/ })()
;
//# sourceMappingURL=iframeSessionScript.js.map