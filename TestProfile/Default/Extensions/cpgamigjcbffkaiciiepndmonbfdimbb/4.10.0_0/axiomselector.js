/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 2205
(module, __unused_webpack_exports, __webpack_require__) {

/*! https://mths.be/cssescape v1.5.1 by @mathias | MIT license */
;(function(root, factory) {
	// https://github.com/umdjs/umd/blob/master/returnExports.js
	if (true) {
		// For Node.js.
		module.exports = factory(root);
	} else // removed by dead control flow
{}
}(typeof __webpack_require__.g != 'undefined' ? __webpack_require__.g : this, function(root) {

	if (root.CSS && root.CSS.escape) {
		return root.CSS.escape;
	}

	// https://drafts.csswg.org/cssom/#serialize-an-identifier
	var cssEscape = function(value) {
		if (arguments.length == 0) {
			throw new TypeError('`CSS.escape` requires an argument.');
		}
		var string = String(value);
		var length = string.length;
		var index = -1;
		var codeUnit;
		var result = '';
		var firstCodeUnit = string.charCodeAt(0);
		while (++index < length) {
			codeUnit = string.charCodeAt(index);
			// Note: there’s no need to special-case astral symbols, surrogate
			// pairs, or lone surrogates.

			// If the character is NULL (U+0000), then the REPLACEMENT CHARACTER
			// (U+FFFD).
			if (codeUnit == 0x0000) {
				result += '\uFFFD';
				continue;
			}

			if (
				// If the character is in the range [\1-\1F] (U+0001 to U+001F) or is
				// U+007F, […]
				(codeUnit >= 0x0001 && codeUnit <= 0x001F) || codeUnit == 0x007F ||
				// If the character is the first character and is in the range [0-9]
				// (U+0030 to U+0039), […]
				(index == 0 && codeUnit >= 0x0030 && codeUnit <= 0x0039) ||
				// If the character is the second character and is in the range [0-9]
				// (U+0030 to U+0039) and the first character is a `-` (U+002D), […]
				(
					index == 1 &&
					codeUnit >= 0x0030 && codeUnit <= 0x0039 &&
					firstCodeUnit == 0x002D
				)
			) {
				// https://drafts.csswg.org/cssom/#escape-a-character-as-code-point
				result += '\\' + codeUnit.toString(16) + ' ';
				continue;
			}

			if (
				// If the character is the first character and is a `-` (U+002D), and
				// there is no second character, […]
				index == 0 &&
				length == 1 &&
				codeUnit == 0x002D
			) {
				result += '\\' + string.charAt(index);
				continue;
			}

			// If the character is not handled by one of the above rules and is
			// greater than or equal to U+0080, is `-` (U+002D) or `_` (U+005F), or
			// is in one of the ranges [0-9] (U+0030 to U+0039), [A-Z] (U+0041 to
			// U+005A), or [a-z] (U+0061 to U+007A), […]
			if (
				codeUnit >= 0x0080 ||
				codeUnit == 0x002D ||
				codeUnit == 0x005F ||
				codeUnit >= 0x0030 && codeUnit <= 0x0039 ||
				codeUnit >= 0x0041 && codeUnit <= 0x005A ||
				codeUnit >= 0x0061 && codeUnit <= 0x007A
			) {
				// the character itself
				result += string.charAt(index);
				continue;
			}

			// Otherwise, the escaped character.
			// https://drafts.csswg.org/cssom/#escape-a-character
			result += '\\' + string.charAt(index);

		}
		return result;
	};

	if (!root.CSS) {
		root.CSS = {};
	}

	root.CSS.escape = cssEscape;
	return cssEscape;

}));


/***/ },

/***/ 4369
(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   AxiomApiHelper: () => (/* binding */ AxiomApiHelper)
/* harmony export */ });
/* harmony import */ var _classes_models_RunningData__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(40575);
/* harmony import */ var _classes_models_RunningData__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_classes_models_RunningData__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _axiombuilder_models_WidgetsNestable__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(35812);



/**
 * Helper functions for running axioms
 *
 */
class AxiomApiHelper {

    /**
     * Transpose table data - swapping rows and columns
     * @param {*} array a 2D array e.g. [[item1a, item1b], [item2a, item2b]]
     * @example AxiomApiHelper.transpose([[item1a, item1b], [item2a, item2b]])
     * @returns a 2D array e.g. [[item1a, item2a], [item1b, item2b]]
     */
    static transpose(array) {
        let subArrayLength = 0
        let newArray = []
        for (let i = 0; i < array.length; i++) {
            if (array[i].length > subArrayLength) {
                subArrayLength = array[i].length
            }
        }
        for (let i = 0; i < subArrayLength; i++) {
            newArray.push([]);
        }
        for (let i = 0; i < array.length; i++) {
            for(let j = 0; j < subArrayLength; j++) {
                let jn = parseInt(j)
                newArray[jn].push(array[i][jn])
            }
        }

        return newArray;
    }

    /** 
    *
    * Introduce a delay with a promise
    * @param time - The time in milliseconds to delay
    *
    */

    static delay(time, v) {
        return new Promise(function(resolve) { 
            setTimeout(resolve.bind(null, v), time)
        });
     }

    /**
     * Convert a numerical index value into the column letter format
     * used by spreadsheet applications i.e. 0 => 'A', 26 => 'AA', 30 => 'AE'
     * @param {*} index the index of the column you want the corresponding column letter for e.g. 0
     * @example AxiomApiHelper.getColLetter(30)
     * @result a string representing the column in a spreadsheet that corresponds to the numerical index given e.g. 'AE'
     */
    static getColLetter(index) {
        let ALPHA = ['!', 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'];

        let base = ALPHA.length-1
        let n = index

        let done = false
        let res = []
        let colLetters = ''

        while (!done) {
            let a = (n / base)
            let remainder = (n % base)
            if (res.length == 0) {
                remainder += 1
            }
            res.push(remainder)
            colLetters = ALPHA[remainder] + colLetters
            n = Math.round(a - (remainder / base))
            done = (n == 0)
        }

        return colLetters
    }

    /**
     * Convert the column letter format value into a numerical index
     * used by spreadsheet applications i.e. 'A' => 0, 'AA' => 26, 'AE' => 30
     * @param {*} colLetters
     * @example AxiomApiHelper.getColIndex('AE')
     * @returns a numerical index e.g. 30
     */
    static getColIndex(colLetters) {
        if (!colLetters) {
            return -1
        }
        colLetters = colLetters.trim()
        if (parseInt(colLetters, 10) >= 0) {
            return colLetters
        }
        let s_numbers = [0];
        for (let i = 0; i < colLetters.length; i++) {
            let pow = Math.pow(26, colLetters.length - i - 1)
            s_numbers[i] = (colLetters[i].charCodeAt(0) - 64) * pow
        }
        return s_numbers.reduce((accumulator, a) => {return accumulator + a}) - 1
    }

    /**
     * Check whether a 2D array contains a 1D array
     *
     * usefull for checking whether row data exists in table data
     *
     * If columns are provided as a param then
     * the arrays will only be compared by the contents of those columns
     * and not the entire contents of each array
     * @param {*} array1 a single dimensional array e.g. ["A", "Example A"]
     * @param {*} array2 a two dimensional array e.g. [["A", "Example A"], ["B", "Example B"]]
     * @param {*} columns an array of column letters to compare by
     * @example AxiomApiHelper.inArray(["A", "Example A"], [["A", "Example A"], ["B", "Example B"]])
     * @returns a boolean value e.g. true
     */
    static inArray(array1, array2, columns = null) {
        let found = false

        for (let array of array2) {
            if (this.matchingArrays(array, array1, columns)) {
                found = true
            }
        }
        return found
    }

    static colString2indexArray(cols) {
        let indeces = []
        for (let col of cols.split(',')) {
            col = col.trim()
            if (Number.isInteger(col)) {
                col = col -1
            } else {
                if (/[A-Za-z]/.test(col)) {
                    if (/[a-z]/.test(col)) {
                        col = col.toUpperCase()
                    }
                    col = this.getColIndex(col)
                } else {
                    col = Number(col) - 1
                }
            }
            if (col > -1){
                indeces.push(col)
            }
        }

        return indeces
    }

    /**
     * Checks whether two single dimensional arrays match - for comparing whether two rows of data match
     *
     * If columns are provided as a param then
     * the arrays will only be compared by the contents of those columns
     * and not the entire contents of each array
     * @param {*} array1 the first array to compare
     * @param {*} array2 the second array to compare against
     * @param {*} columns an array of columns letters to compare within each array e.g. ['A','D']
     * @example AxiomApiHelper.matchingArrays([0,0,0,0], [0,2,1,0], ['A','D'])
     * @return a boolean value e.g. true
     */
    static matchingArrays(array1, array2, columns = null) {
        let singleDimension = true
        if (array1.length != array2.length) {
            return false
        }
        if (Array.isArray(array1) != Array.isArray(array2)) {
            return false
        } else {
            if (Array.isArray(array1)) {
                singleDimension = false
            }
        }
        let matching = true

        if (Array.isArray(columns) && columns.length > 0) {
        } else {
            columns = []
            let tableWidth = (array1.length > array2.length) ? array1.length : array2.length
            for (let i = 0; i < tableWidth; i ++) {
                columns.push(this.getColLetter(i+1))
            }
        }

        for (let colLetters of columns) {
            let i = this.getColIndex(colLetters)

            if (array1[i] != array2[i]) {
                matching = false
            }
        }

        return matching
    }

    static clone(array) {
        if (!array) {
            return [[""]]
        }
        let cloned = []
        if (Array.isArray(array[0])) {
            for (let item of array) {
                cloned[array.indexOf(item)] = this.clone(item)
            }
        } else {
            for (let key of Object.keys(array)) {
                cloned[key] = array[key].valueOf()
            }
        }
        return cloned
    }

    static getRoute(url) {
        let domain = url
        if (/\/\//.test(url)) {
            var split = url.split('//')
            var protocol = split[0]
            domain = split[split.length -1]
            var domainSegs = domain.split('.')
            if (domainSegs.length > 2) {
                var net = domainSegs.shift()
            }
            let route = domainSegs.pop()
            route = route.split('/')
            route.pop()
            domain = domainSegs.join('.') + '.' + route.join('/')
        }
        return domain
    }

    /**
     * Send a message to the tab window.
     */
    static sendTabMessage(action, params) {
        return new Promise((resolve, reject) => {
            let rd = new (_classes_models_RunningData__WEBPACK_IMPORTED_MODULE_0___default())()
            rd.load().then(async () => {
                let tab_id
                try { 
                    tab_id = rd.states[0].tab_id
                } catch (e) {
                    // To stop javascript doing its normal idiot thing
                }
                if (!tab_id) {
                    // If we have no tab id, try and find one in which axiom is loaded
                    tab_id = await new Promise(resolve2 => {
                        chrome.tabs.query({}, (tabs) => {
                            for (let tab of tabs) {
                                chrome.tabs.sendMessage(tab.id, {action: 'is_loaded'}, response => {
                                    if (response) {
                                        resolve2(tab.id)
                                    }
                                })
                            }
                        })
                        setTimeout(() => {
                            resolve2(null)
                        }, 2000)
                    })
                }
                params.action = action
                chrome.tabs.sendMessage(tab_id, params, response => {
                    if (chrome.runtime.hasOwnProperty("lastError")) {
                        switch (action) {
                            case "display_message":
                                resolve('')
                                break
                            default:
                                resolve({error: {message: chrome.runtime.lastError.message}})
                                break
                        }
                    } else {
                        resolve(response)
                    }
                })
            })
        })
    }

    static isValidJson(str) {
        try {
            const obj = JSON.parse(str)

            if (obj && typeof obj === 'object') {
                return true
            }
        } catch (e) {
        }

        return false
    }

    static buildSelectorArray(selector, resultType) {
        let selectors = []
        let resultTypes = []
        if (!Array.isArray(selector)) {
            if (typeof selector === 'string') {
                selectors = selector.split(',')// TODO - replace with split
                let trimmed = []
                for (let s of selectors) {
                    trimmed.push(s.trim())
                    if (typeof resultType === 'string') {
                        resultTypes.push(resultType)
                    } else {
                        resultTypes.push('textContent')
                    }
                }
                selectors = trimmed
            }
        } else {
            if (selector[0].resultType !== undefined) {
                resultTypes = selector.map(s => {
                    return s.resultType
                })
                selectors = selector.map(s => {
                    return s.selector
                })
            }
        }
        return {selectors, resultTypes}
    }

    static applyToIframes(callback) {
        jQuery('iframe').each((index, el) => {
            const content = jQuery(el).contents()
            if (content && content.length) {
                callback(index, content)
            }
        })
    }

    /**
     * Extracts form data from an axiom / task object
     * @param {} task 
     */
    static extractFormData(task, keepDisabled = false) {
        let formData = []
        while (typeof task.data === 'string') {
            task.data = JSON.parse(task.data)
        }
        // remove all disabled widgets from task before run.
        // used `for in` to take the index
        for (let wid in task.data.form) {
            if(keepDisabled || !(task.data.form[wid].is_disable !== undefined && task.data.form[wid].is_disable === true)) {
                formData.push(task.data.form[wid])
            }
        }
        return formData
    }

    /**
     * Loads the campaign cookie from the Axiom website, if one is set
     */
    static async getCampaign() {
        return new Promise(resolve => {
            chrome.cookies.getAll({name: "axiom_ga_query_params"}, res => {
                if (res.length > 0) {
                    const desiredCookie = res.filter(item => item.path === '/')[0]
                    if (desiredCookie) {
                        resolve(desiredCookie.value)
                    } else {
                        resolve(res[0].value)
                    }
                } else {
                    resolve('')
                }
            })
        })
    }

    static getStepNumbering(widgets, nestingData) {
        if (!nestingData) {
            const wn = new _axiombuilder_models_WidgetsNestable__WEBPACK_IMPORTED_MODULE_1__.WidgetsNestable()
            nestingData = wn.buildNestingData(widgets)
        }
        let parts = [0, 0, 0, 0, 0]
        for (let windex in nestingData) {
            if (!nestingData[windex].endingBlock) {
                parts[nestingData[windex].indent]++
            } else if (nestingData[windex-1] && nestingData[windex-1].indent > nestingData[windex].indent) {
                parts[nestingData[windex-1].indent] = 0
            }
            widgets[windex].stepNumber = parts.slice(0, nestingData[windex].indent + 1).join('.')
        }
    }

    static getTrimmedUrl(url) {
        try {
            let trimmed = url.trim().toLowerCase()
            let urlObject = new URL(trimmed)

            urlObject.hash = ''
            urlObject.search = ''
            urlObject.pathname = ''

            return urlObject.toString()
        } catch(e) {
            return url
        }
    }

    /**
     * Export the current page HTML to a downloadable file
     * @param {string} filename Optional custom filename
     * @returns {Promise} Promise that resolves when export is complete
     */
    static exportCurrentPageHTML(filename = null) {
        return this.sendTabMessage('export_page_html', {filename: filename})
    }
}


/***/ },

/***/ 11258
(__unused_webpack_module, exports) {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.ScrapeHelper = void 0;
var ScrapeHelper = /** @class */ (function () {
    function ScrapeHelper() {
        // This generates and stores the grouping selector when a preview is being built. Used later to visually highlight the grouping.
        this.groupSelector = "";
    }
    ScrapeHelper.prototype.getPreview = function (doc, selectors, resultTypes) {
        if (selectors && selectors.length > 0 && selectors[0] !== "No valid path found." && /[^\[\]"']/g.test(JSON.stringify(selectors))) {
            var traces = this.mapTraces(doc, selectors, resultTypes);
            if (Array.isArray(traces)) {
                return traces;
            }
            else {
                return [];
            }
        }
        else {
            return [[]];
        }
    };
    ScrapeHelper.prototype.getDataV0210 = function (el, resultType) {
        var data = '';
        switch (resultType) { //TODO: review all result types
            case 'outerHTML':
                data = el.outerHTML;
                break;
            case 'innerHTML':
                data = el.innerHTML;
                if (!data) {
                    data = el.outerHTML;
                }
                break;
            case 'textContent':
                data = '';
                var text = el['innerText'];
                if (typeof (text !== 'text')) {
                    text = String(text);
                }
                if (text) {
                    data = text.trim();
                }
                if (data === '') {
                    try {
                        var el2 = el;
                        data = el2.value.trim();
                    }
                    catch (e) {
                        // Stop execution from finishing here if there's an error
                    }
                }
                break;
            case 'link': //TODO: expand to match custom link result type in scraper
            case 'href':
                var linkEl = el;
                if (!el.hasAttribute('href')) {
                    var children = el.querySelectorAll('[href]');
                    if (children && children.length) {
                        linkEl = children[0];
                    }
                }
                var href = null;
                if (linkEl.hasAttribute('href')) {
                    href = linkEl['href'];
                }
                data = (href !== null) ? href : '';
                break;
            case 'image':
                var imgEl = el;
                if (!el.hasAttribute('src') && !el.hasAttribute('srcset')) {
                    var children = Array.from(el.querySelectorAll('[src]')).concat(Array.from(el.querySelectorAll('[srcset]')));
                    if (children && children.length) {
                        // According to Barlow, the last item is "almost always" correct, but this isn't really possible to determine without some extra UI
                        imgEl = children[children.length - 1];
                    }
                }
                var src = null;
                if (imgEl.hasAttribute('src')) {
                    src = imgEl['src'];
                }
                else if (imgEl.hasAttribute('srcset')) {
                    src = imgEl['srcset'];
                }
                data = (src !== null) ? src : '';
                break;
        }
        return data;
    };
    ScrapeHelper.prototype.getData = function (el, resultType) {
        var scrapeLink = (resultType === "link" || resultType === 'href');
        resultType = (scrapeLink) ? "outerHTML" : resultType;
        var result = el[resultType];
        if (scrapeLink) {
            var i = 1;
            var res = '';
            while (res == "" && i <= 5) {
                result = el[resultType];
                var href = el['href'];
                var link = void 0;
                if (href && href.match(/(([A-Za-z]+[:][/][/])|([/][^"' ])).[^"' ]+[^"' ]+([^"' ])/)) {
                    link = href;
                }
                else {
                    var resultMatched = result.match(/href=["'](([A-Za-z]+[:][/][/])|([/][^"' ])).[^"' ]+[^"' ]+([^"' ])/);
                    if (resultMatched) {
                        link = resultMatched[0].substring(6);
                    }
                    else {
                        var linkMatched = result.match(/["'](([A-Za-z]+[:][/][/])|([/][^"' ])).[^"' ]+[/]+[^"' ]+([^"' ])/);
                        if (linkMatched) {
                            link = linkMatched[0].substring(1);
                        }
                        else {
                            res = "";
                        }
                    }
                }
                if (link) {
                    if (link[0] == '/') {
                        var url = window.location.href;
                        if (link[1] == '/') {
                            link = url.match(/.[^/]+[/][/]/)[0] + link.substring(2);
                        }
                        else {
                            link = url.match(/[A-Za-z]+[:][/].[^/]+[/]/)[0] + link.substring(1);
                        }
                    }
                    res = (link) ? link : "";
                }
                // If we didn't get a link then instead look at the parent of the current element and try to get a link from that instead
                if (res === "") {
                    var parent = el.parentElement;
                    if (parent && parent.innerHTML) {
                        i++;
                        el = parent;
                    }
                    else {
                        break;
                    }
                }
                else {
                    break;
                }
            }
            result = res;
        }
        return result;
    };
    ScrapeHelper.prototype.countSiblingsLeft = function (el) {
        var siblings = [];
        var n = el;
        var done = false;
        while (!done) {
            var sibling = n.previousElementSibling;
            if (sibling) {
                siblings.push(sibling);
                n = sibling;
            }
            else {
                done = true;
            }
        }
        return siblings.length;
    };
    ScrapeHelper.prototype.getRootTree = function (el) {
        var rootTree = [];
        var node = el;
        var done = false;
        while (!done) {
            var nthCount = this.countSiblingsLeft(node);
            rootTree.unshift(nthCount);
            var parent = node.parentElement;
            if (parent) {
                node = parent;
            }
            else {
                done = true;
            }
        }
        return rootTree;
    };
    ScrapeHelper.prototype.tracesEqual = function (a, b, depth) {
        if (!a || !b) {
            return false;
        }
        for (var i = 0; i < depth; i++) {
            if (a[i] !== b[i]) {
                return false;
            }
        }
        return true;
    };
    ScrapeHelper.prototype.attemptGroups = function (all_res, gDepth) {
        var groups = [];
        var grouped = [];
        var lastRow = 0;
        var rowToAddTo = null;
        for (var _i = 0, all_res_1 = all_res; _i < all_res_1.length; _i++) {
            var res = all_res_1[_i];
            grouped.push([]);
            for (var _a = 0, res_1 = res; _a < res_1.length; _a++) {
                var item = res_1[_a];
                var colsProcessed = 0;
                // OK, so we need to check this item's trace against items not in this column to find a matching trace.
                // If we find the matching row, insert our item there and stop. If we fall off the end, push the new row instead.
                var traceMatchFound = false;
                for (var g = 0; g < grouped.length - 1; g++) {
                    var colProcessed = 0;
                    for (var i = 0; i < grouped[g].length; i++) {
                        if (grouped[g][i] && item.trace) {
                            colProcessed = 1;
                            traceMatchFound = this.tracesEqual(grouped[g][i].trace, item.trace, gDepth);
                            if (traceMatchFound) {
                                rowToAddTo = i;
                                break;
                            }
                        }
                    }
                    colsProcessed += colProcessed;
                    if (traceMatchFound)
                        break;
                }
                if (colsProcessed === 1) {
                    // If only one column has been processed, we basically want to ignore the grouping and just push the columns straight onto its row
                    grouped[grouped.length - 1].push(item);
                }
                else if (grouped.length > 1 && lastRow === 1) {
                    // We automatically assume this is a grouping match if there's more than one column but only one row
                    grouped[grouped.length - 1][lastRow - 1] = item;
                }
                else if (!traceMatchFound) {
                    // If a trace match was not found, increase the number of rows and place on a new row
                    grouped[grouped.length - 1][lastRow] = item;
                    lastRow++;
                }
                else {
                    // A trace match has been found, so let's add to the correct row
                    grouped[grouped.length - 1][rowToAddTo] = item;
                    if (rowToAddTo > lastRow)
                        lastRow = rowToAddTo;
                }
            }
        }
        for (var sg in grouped) {
            for (var it in grouped[sg]) {
                if (!groups[it]) {
                    groups[it] = [];
                }
                groups[it][sg] = grouped[sg][it].data;
            }
        }
        // Clean up empty items
        for (var r = 0; r < groups.length; r++) {
            for (var c = 0; c < groups[r].length; c++) {
                if (!groups[r][c]) {
                    groups[r][c] = '';
                }
            }
        }
        return groups;
    };
    ScrapeHelper.prototype.mapTraces = function (doc, selectors, resultTypes) {
        if (resultTypes === void 0) { resultTypes = "textContent"; }
        // Do nothing, change nothing if document is not set
        if (!doc || !doc.querySelectorAll) {
            return { 0: [] };
        }
        var gDepthMod = 0;
        var tides = [];
        var all_res = [];
        // if we only have one result type provided then we should use that for all selectors
        if (typeof resultTypes === 'string') {
            var resultType = resultTypes.valueOf();
            resultTypes = [];
            for (var _i = 0, selectors_1 = selectors; _i < selectors_1.length; _i++) {
                var s = selectors_1[_i];
                resultTypes.push(resultType);
            }
        }
        for (var s = 0; s < selectors.length; s++) {
            var selector = selectors[s];
            var resultType = resultTypes[s];
            if (selector && selector.length > 0) {
                try {
                    if (selector === 'head' || !selector) {
                        throw ('');
                    }
                    var els = Array.from(doc.querySelectorAll(selector));
                    if (!els || els.length === 0) {
                        // A missing element returns "NO MATCHING ELEMENT"; this is used later in comparing results from different iframes to choose the best outcome
                        throw ('NO MATCHING ELEMENT');
                    }
                    if (els.length === 1) {
                        gDepthMod -= 1;
                    }
                    var results = [];
                    for (var _a = 0, els_1 = els; _a < els_1.length; _a++) {
                        var el = els_1[_a];
                        var e = els.indexOf(el);
                        var data = this.getDataV0210(el, resultType);
                        if (!data) {
                            data = "No data, change column type or re-select";
                        }
                        var tag = 'axiom' + s + '-' + e;
                        var trace = this.getRootTree(el);
                        el.className = el.className.replace("axiom-matched", '');
                        results.push({ trace: trace, data: data, selector: selector, tag: tag, el: el });
                    }
                    var minTide = results[0].trace.length;
                    var maxTide = 0;
                    for (var r = 0; r < results.length; r++) {
                        var trace = results[r].trace;
                        var prev = results[results.length - 1].trace;
                        if (r > 0) {
                            prev = results[r - 1].trace;
                        }
                        var tide = 0;
                        var done = false;
                        while (!done && tide < trace.length) {
                            var t_depth = trace[tide];
                            var p_depth = prev[tide];
                            if (t_depth !== p_depth) {
                                done = true;
                            }
                            tide++;
                        }
                        if (tide < minTide) {
                            minTide = tide;
                        }
                        if (tide > maxTide) {
                            maxTide = tide;
                        }
                        results[r].trace.push(tide);
                    }
                    tides.push({ minTide: minTide, maxTide: maxTide });
                    all_res.push(results);
                }
                catch (e) {
                    tides.push({ minTide: 999, maxTide: 999 });
                    all_res.push([{ trace: null, data: e, selector: selector, tag: null, el: null }]);
                }
            }
        }
        if (tides.length && all_res.length) {
            tides.sort(function (a, b) {
                return a.maxTide - b.maxTide;
            });
            var gDepth = tides[0].maxTide;
            gDepth += gDepthMod;
            this.generateGroupSelector(all_res, gDepth);
            var grouped = this.attemptGroups(all_res, gDepth);
            return grouped;
        }
        else {
            return { 0: [] };
        }
    };
    ScrapeHelper.prototype.generateGroupSelector = function (all_res, gDepth) {
        this.groupSelector = "";
        if (!all_res || !all_res[0] || !all_res[0][0] || !all_res[0][0].trace) {
            return;
        }
        for (var i = 0; i < gDepth; i++) {
            if (i > 0) {
                this.groupSelector += " > ";
            }
            this.groupSelector += ":-webkit-any(*):nth-child(" + parseInt(all_res[0][0].trace[i] + 1) + ")";
        }
    };
    return ScrapeHelper;
}());
exports.ScrapeHelper = ScrapeHelper;


/***/ },

/***/ 13442
(__unused_webpack_module, exports) {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
/**
 * Fetches the parent of the element in a string format
 */
var IdSelector = /** @class */ (function () {
    function IdSelector() {
    }
    IdSelector.prototype.getSelector = function (el) {
        return "#".concat(el.id);
    };
    return IdSelector;
}());
exports["default"] = IdSelector;


/***/ },

/***/ 21149
(__unused_webpack_module, exports) {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
var ClassSelector = /** @class */ (function () {
    function ClassSelector() {
    }
    ClassSelector.prototype.getSelector = function (el) {
        if (!el) {
            return;
        }
        var classes = el.getAttribute('class') || '';
        classes = classes.replace(/axiom-matched|axiom-suggested-group|axiom-link|axiom-download|axiom-sel-\S+|selectorgadget_\w+/g, '').trim();
        if (classes !== '') {
            classes = '.' + classes.replace(/\s+/g, '.');
        }
        return classes;
    };
    return ClassSelector;
}());
exports["default"] = ClassSelector;


/***/ },

/***/ 33729
(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.InjectedSelectorTool = void 0;
var AttributeSelector_1 = __webpack_require__(78889);
var HierachyActions_1 = __webpack_require__(89362);
var SelectorFacade_1 = __webpack_require__(68037);
var BorderHighlight_1 = __webpack_require__(41510);
var ScrapeHelper_1 = __webpack_require__(11258);
var AxiomApiHelper_1 = __webpack_require__(4369);
/**
 * SelectionActions
 */
var SelectionActions = /** @class */ (function () {
    function SelectionActions(context) {
        this.selectorData = context;
    }
    SelectionActions.prototype.add_column = function (request) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                this.selectorData.addSelector();
                this.selectorData.editSelector(this.selectorData.selectors.length - 1);
                return [2 /*return*/];
            });
        });
    };
    SelectionActions.prototype.remove_column = function (request) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                this.selectorData.removeSelector(request.index);
                return [2 /*return*/];
            });
        });
    };
    SelectionActions.prototype.select_column = function (request) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                this.selectorData.editSelector(request.index);
                return [2 /*return*/];
            });
        });
    };
    SelectionActions.prototype.set_result_type = function (request) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                this.selectorData.setResultType(request.sel_index, request.resultType);
                return [2 /*return*/];
            });
        });
    };
    SelectionActions.prototype.reset_column = function (request) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                this.selectorData.resetSelector(request.index);
                this.selectorData.editSelector(request.index);
                return [2 /*return*/];
            });
        });
    };
    SelectionActions.prototype.addElementToSelection = function (request) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2 /*return*/];
            });
        });
    };
    SelectionActions.prototype.removeElementFromSelection = function (request) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2 /*return*/];
            });
        });
    };
    SelectionActions.prototype.edit_selector = function (request) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                this.selectorData.updateSelector(request.index, request.selector, request.target);
                return [2 /*return*/];
            });
        });
    };
    return SelectionActions;
}());
/**
 * SelectorData
 */
var SelectorData = /** @class */ (function () {
    function SelectorData() {
        this.refreshRequired = false;
        this.selectors = null;
        this.activeSelectorIndex = 0;
        this.actions = new SelectionActions(this);
    }
    /**
     * Executes the requested action and then automatically handles any recalculations and issuing of updates
     *
     * @param request {action, ...params}
     */
    SelectorData.prototype.actionRequest = function (request) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.actions[request.action](request)];
                    case 1:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    SelectorData.prototype.addSelector = function () {
        this.selectors.push({
            selector: 'head',
            selectedElements: [],
            rejectedElements: [],
            resultType: this.defaultResultType
        });
        this.refreshRequired = true;
    };
    SelectorData.prototype.removeSelector = function (index) {
        this.selectors.splice(index, 1);
        if (this.selectors.length === 0) {
            this.addSelector();
        }
        else {
            var removedLastColumn = (index === this.selectors.length);
            var removedWhileSelected = (index === this.activeSelectorIndex);
            var selectedColumnShiftedLeft = (index <= this.activeSelectorIndex);
            if ((removedLastColumn && removedWhileSelected) || selectedColumnShiftedLeft) {
                this.editSelector(this.activeSelectorIndex - 1);
            }
        }
        if (this.activeSelectorIndex === -1 && this.selectors.length > 0) {
            this.activeSelectorIndex = 0;
        }
        this.refreshRequired = true;
    };
    SelectorData.prototype.editSelector = function (index) {
        if (index < this.selectors.length) { // check index exists
            this.activeSelectorIndex = index;
        }
        else if (this.activeSelectorIndex >= this.selectors.length) {
            // if current selection is not valid then set to last column
            this.activeSelectorIndex = this.selectors.length - 1;
        }
        this.refreshRequired = true;
    };
    SelectorData.prototype.updateSelector = function (index, selector, target) {
        if (!this.selectors[index]) {
            // Only happens if it's a brand new scrape, so this should be safe
            this.addSelector();
        }
        this.selectors[index] = selector[index];
        var singleSelector = new SelectorFacade_1.SelectorFacade();
        if (target === "hierarchy") {
            var el = document.querySelector(selector[index].selector.hierarchy);
            if (!el) {
                this.selectors[index].selector.innerText = "",
                    this.selectors[index].selector.targetElement = undefined;
                return;
            }
            var newSelectors = singleSelector.getSelector(el);
            this.selectors[index].selector.innerText = newSelectors.innerText,
                this.selectors[index].selector.targetElement = newSelectors.targetElement;
        }
        else if (target === "innerText") {
            var el = document.evaluate("//*[text()='" + selector[index].selector.innerText + "']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (!el) {
                this.selectors[index].selector.hierarchy = "";
                this.selectors[index].targetElement = undefined;
                return;
            }
            var newSelectors = singleSelector.getSelector(el);
            this.selectors[index].selector.hierarchy = newSelectors.hierarchy;
            this.selectors[index].selector.targetElement = newSelectors.targetElement;
        }
        this.refreshRequired = true;
    };
    SelectorData.prototype.setResultType = function (index, resultType) {
        if (!this.selectors[index]) {
            this.addSelector();
        }
        this.activeSelectorIndex = index;
        this.selectors[index].resultType = resultType;
        this.refreshRequired = true;
    };
    SelectorData.prototype.resetSelector = function (index) {
        this.selectors[index] = {
            selector: 'head',
            selections: [],
            selectedElements: [],
            rejectedElements: [],
            resultType: this.defaultResultType,
            groupSelector: 'body'
        };
        this.refreshRequired = true;
    };
    return SelectorData;
}());
/**
 * @author Nasik aka Kisan <nasik.shafeek@abstraction.co>
 * @author Simon Delany <simon.delany@axiom.ai>
 *
 * Injected into content page and will be kicked into action when the tool is in use
 *
 */
var InjectedSelectorTool = /** @class */ (function () {
    function InjectedSelectorTool() {
        var _this = this;
        this.iframeHighlightBorders = [];
        this.lastSelectorId = 0;
        this.activeSelector = [];
        this.activeSelectorIndex = -1;
        this.selectingClass = 'axiom-sel-selected-';
        this.suggestingClass = 'axiom-sel-suggested-';
        this.rejectingClass = 'axiom-sel-rejected-';
        this.resultType = 'textContent';
        this.resultTypes = ['textContent'];
        this.iframeSupportEnabled = false;
        this.SelectorAlgorithm = new AttributeSelector_1.AttributeSelector();
        this.hierarchyActions = new HierachyActions_1.HierarchyActions();
        this.matching = [];
        this.matchingData = [];
        this.highlightBorder = new BorderHighlight_1.BorderHighlight(document, false, false);
        this.singleSelector = new SelectorFacade_1.SelectorFacade();
        this.scrapeHelper = new ScrapeHelper_1.ScrapeHelper();
        this.selectorData = new SelectorData();
        chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) { return __awaiter(_this, void 0, void 0, function () {
            var _a, suggestions;
            var _this = this;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        _a = request.action;
                        switch (_a) {
                            case 'selector_tool_start': return [3 /*break*/, 1];
                            case 'selector_tool_confirm': return [3 /*break*/, 2];
                            case "selector_tool_reset": return [3 /*break*/, 3];
                            case "selector_tool_cancel": return [3 /*break*/, 4];
                            case "set_result_type": return [3 /*break*/, 5];
                            case 'select_column': return [3 /*break*/, 5];
                            case 'remove_column': return [3 /*break*/, 5];
                            case 'add_column': return [3 /*break*/, 5];
                            case 'reset_column': return [3 /*break*/, 5];
                            case 'edit_selector': return [3 /*break*/, 5];
                            case "hide_bubble": return [3 /*break*/, 7];
                            case "generate_suggestions": return [3 /*break*/, 8];
                            case "set_iframe_support": return [3 /*break*/, 9];
                        }
                        return [3 /*break*/, 10];
                    case 1:
                        this.scrapeHelper.groupSelector = "";
                        this.selectionMode = (request.selectionType === 'smart' || request.selectionType === 'multi') ? 'multiple' : 'single';
                        if (request.resultType) {
                            if (Array.isArray(request.resultType)) {
                                this.resultTypes = request.resultType;
                                this.resultType = this.resultTypes[this.selectorData.activeSelectorIndex];
                            }
                            else {
                                this.resultType = request.resultType;
                                this.resultTypes = [request.resultType];
                            }
                        }
                        else {
                            this.resultType = 'outerHTML';
                        }
                        // We have to set a default resultType e.g. for widgets like scrapeLink to have the link result type as default
                        this.selectorData.defaultResultType = this.resultType; // this sets a default result type for this selection. any time you add a column it will default this this resultType.
                        this.highlightBorder.updateResultType(this.resultType);
                        this.highlightBorder.updateWindex(request.windex);
                        this.injectV0200();
                        if (!request.selectors) {
                            return [2 /*return*/];
                        }
                        if (this.selectionMode === "multiple") {
                            this.selectorData.selectors = request.selectors;
                            this.selectionMode = 'multiple';
                            this.updateSelections(this.selectorData.selectors[this.selectorData.activeSelectorIndex].resultType, this.selectorData.activeSelectorIndex, document);
                            AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, content) {
                                _this.updateSelections(_this.selectorData.selectors[_this.selectorData.activeSelectorIndex].resultType, _this.selectorData.activeSelectorIndex, content[0]);
                            });
                            this.sendStateUpdate();
                        }
                        else if (this.selectionMode === 'single') {
                            this.selectorData.selectors = request.selectors;
                            this.resetHighlights(document);
                            AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, content) {
                                _this.resetHighlights(content[0]);
                            });
                        }
                        return [3 /*break*/, 10];
                    case 2:
                        if (!request.template_mode) {
                            this.closingAction(request.widget_type);
                        }
                        sendResponse(this.selectorData.selectors);
                        this.ejectV0200();
                        return [3 /*break*/, 10];
                    case 3:
                        this.ejectV0200();
                        this.selectionMode = (request.selectionType === 'smart' || request.selectionType === 'multi') ? 'multiple' : 'single';
                        this.injectV0200();
                        return [3 /*break*/, 10];
                    case 4:
                        this.ejectV0200();
                        return [3 /*break*/, 10];
                    case 5:
                        this.removeAllHighlights(document);
                        AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, doc) {
                            _this.removeAllHighlights(doc);
                        });
                        return [4 /*yield*/, this.selectorData.actionRequest(request)];
                    case 6:
                        _b.sent();
                        if (this.selectionMode === 'multiple') {
                            if (this.selectorData.refreshRequired && this.selectorData.selectors[this.selectorData.activeSelectorIndex]) {
                                this.updateSelections(this.selectorData.selectors[this.selectorData.activeSelectorIndex].resultType, this.selectorData.activeSelectorIndex, document);
                                AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, content) {
                                    _this.updateSelections(_this.selectorData.selectors[_this.selectorData.activeSelectorIndex].resultType, _this.selectorData.activeSelectorIndex, content[0]);
                                });
                                this.sendStateUpdate();
                            }
                        }
                        else if (this.selectionMode === 'single') {
                            this.resetHighlights(document);
                            AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, content) {
                                _this.resetHighlights(content[0]);
                            });
                            this.sendStateUpdate();
                        }
                        return [3 /*break*/, 10];
                    case 7:
                        chrome.runtime.sendMessage({ action: 'cancel_preview' });
                        this.ejectV0200();
                        return [3 /*break*/, 10];
                    case 8:
                        suggestions = this.generateSuggestions(request.selector);
                        sendResponse({ suggestions: suggestions });
                        return [3 /*break*/, 10];
                    case 9:
                        this.iframeSupportEnabled = request.value;
                        this.iframeHighlightBorders.forEach(function (item) {
                            item.setIframeSupportEnabled(request.value);
                        });
                        return [3 /*break*/, 10];
                    case 10: return [2 /*return*/];
                }
            });
        }); });
    }
    InjectedSelectorTool.prototype.generateSuggestions = function (selector) {
        if (!selector || selector === "head") {
            return [];
        }
        var results;
        try {
            results = document.querySelectorAll(selector);
        }
        catch (e) {
            return [];
        }
        var sharedAttributes = [];
        var combinedSelector = this.hierarchyActions.getCombined(document, Array.from(results), [], 'selector');
        sharedAttributes.push(combinedSelector);
        for (var i in results) {
            var el = results[i];
            if (sharedAttributes.length === 1) {
                if (el.attributes) {
                    for (var _i = 0, _a = el.attributes; _i < _a.length; _i++) {
                        var attr = _a[_i];
                        if (attr.name !== "class" && attr.value) {
                            var as = this.createAttributeSelector(attr);
                            if (this.testGeneratedSelector(as, results.length)) {
                                sharedAttributes.push(as);
                            }
                        }
                    }
                }
                if (el.classList) {
                    for (var _b = 0, _c = el.classList; _b < _c.length; _b++) {
                        var c = _c[_b];
                        if (c.indexOf('axiom') === -1) {
                            if (this.testGeneratedSelector("." + c, results.length)) {
                                sharedAttributes.push("." + c);
                            }
                        }
                    }
                }
            }
            else {
                // This segment basically removes things in the case that the first result happened to have a length match, but it actually doesn't
                // include one of the originally selected results (instead it includes something else).
                if (el.attributes) {
                    for (var _d = 0, _e = el.attributes; _d < _e.length; _d++) {
                        var attr = _e[_d];
                        var as = this.createAttributeSelector(attr);
                        var found = "";
                        for (var sai in sharedAttributes) {
                            if (sharedAttributes[sai] === as) {
                                found = sai;
                                break;
                            }
                        }
                        if (!found) {
                            sharedAttributes[found] = null;
                        }
                    }
                }
                if (el.classList) {
                    for (var _f = 0, _g = el.classList; _f < _g.length; _f++) {
                        var c = _g[_f];
                        var found = "";
                        for (var _h = 0, sharedAttributes_1 = sharedAttributes; _h < sharedAttributes_1.length; _h++) {
                            var sai = sharedAttributes_1[_h];
                            if (sharedAttributes[sai] === "." + c) {
                                found = sai;
                            }
                        }
                        if (!found) {
                            sharedAttributes[found] = null;
                        }
                    }
                }
            }
        }
        sharedAttributes = sharedAttributes.filter(function (el) {
            return el != null;
        });
        return sharedAttributes;
    };
    InjectedSelectorTool.prototype.createAttributeSelector = function (attr) {
        return '[' + attr.name + "='" + attr.value + "']";
    };
    InjectedSelectorTool.prototype.testGeneratedSelector = function (selector, targetLength) {
        if (!selector) {
            return false;
        }
        var r = document.querySelectorAll(selector);
        return r.length === targetLength;
    };
    /**
     * Start Using the tool
     */
    InjectedSelectorTool.prototype.injectV0200 = function () {
        var _this = this;
        this.inuse = true;
        this.selectorData.selectors = [];
        this.selectorData.activeSelectorIndex = 0;
        this.highlightBorder.updateactiveSelectorIndex(0);
        this.highlightBorder.inject();
        if (this.selectionMode === 'single') {
            jQuery(document).on('mousedown.axiom-selection', function (e) {
                _this.singleElementClickHandler(e);
            });
            AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, content) {
                jQuery(content[0]).on('mousedown.axiom-selection', function (e) {
                    _this.singleElementClickHandler(e);
                });
            });
        }
        else {
            // Adding require things to the parent window
            jQuery(document).on('mousedown.axiom-selection', function (e) {
                _this.elementClickHandler(e);
            });
            AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, content) {
                jQuery(content[0]).on('mousedown.axiom-selection', _this.elementClickHandler.bind(_this));
            });
        }
        if (this.resultType === 'link') {
            jQuery('a').addClass('axiom-link');
        }
        else if (this.resultType === 'axiom-download') {
            jQuery('a').addClass('axiom-download');
        }
        /**
         * Linking the css file for highlighting and stuff
         */
        jQuery('body').addClass('axiom-sel-in-action');
        // Adding the required things to each same origin iframe
        AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, content) {
            if (content.length) {
                _this.iframeHighlightBorders[index] = new BorderHighlight_1.BorderHighlight(content[0], true, _this.iframeSupportEnabled);
                _this.iframeHighlightBorders[index].inject();
                var body = content.find('body');
                var stylesheet = chrome.runtime.getURL("axiomselector.css");
                body.append('<link rel="stylesheet" type="text/css" href="' + stylesheet + '">');
                body.addClass('axiom-sel-in-action');
                if (_this.resultType === 'link') {
                    content.find('a').addClass('axiom-link');
                }
                else if (_this.resultType === 'axiom-download') {
                    content.find('a').addClass('axiom-download');
                }
            }
        });
    };
    /**
     * Inject into specific classes where traditional injection doesn't work
     *
     * @param mode string | 'single', 'multiple'
     */
    InjectedSelectorTool.prototype.injectIntoSpecificClasses = function (mode) {
        var algos = {
            'single': this.singleElementClickHandler.bind(this),
            'multiple': this.elementClickHandler.bind(this)
        };
        jQuery('.c9-menu-btn').on('mousedown.axiom-selection', algos[mode]);
    };
    InjectedSelectorTool.prototype.ejectFromSpecificClasses = function () {
        jQuery('.c9-menu-btn').off('mousedown.axiom-selector');
    };
    InjectedSelectorTool.prototype.updateSelections = function (activeResultType, activeSelectorIndex, doc) {
        this.highlightBorder.updateResultType(activeResultType);
        this.highlightBorder.updateactiveSelectorIndex(activeSelectorIndex);
        this.updateActiveResultType();
        this.findMatchesV0190(doc); // TODO: split into the following
        this.setHighlights(doc);
    };
    InjectedSelectorTool.prototype.updateActiveResultType = function () {
        this.resultType = this.selectorData.selectors[this.selectorData.activeSelectorIndex].resultType;
        // remove old result type dependant classes
        jQuery('a').removeClass('axiom-link');
        jQuery('a').removeClass('axiom-download');
        // add current result type dependant classes
        if (this.resultType === 'link') {
            jQuery('a').addClass('axiom-link');
        }
        else if (this.resultType === 'axiom-download') {
            jQuery('a').addClass('axiom-download');
        }
    };
    InjectedSelectorTool.prototype.sendStateUpdate = function (setFocus) {
        if (setFocus === void 0) { setFocus = false; }
        var msg = {
            action: "update_state",
            preview_data: this.matchingData,
            selectors: this.selectorData.selectors,
            activeSelectorIndex: this.selectorData.activeSelectorIndex,
            groupSelector: this.scrapeHelper.groupSelector
        };
        chrome.runtime.sendMessage(msg);
        if (setFocus) {
            // Set focus back to the extension after an element has been selected so that keyboard shortcuts function
            window.focus();
            chrome.runtime.sendMessage({ action: "focus_selector_interface" });
        }
    };
    /**
     * Disables the usage of the tool
     */
    InjectedSelectorTool.prototype.ejectV0200 = function () {
        var _this = this;
        jQuery(document).off('mousedown.axiom-selection');
        jQuery('body').removeClass('axiom-sel-in-action');
        this.removeAllHighlights(document);
        var groupStyle = document.getElementById('axiom-group-style');
        if (groupStyle) {
            document.head.removeChild(groupStyle);
        }
        if (this.highlightBorder) {
            this.highlightBorder.eject();
        }
        jQuery('a').removeClass('axiom-link');
        AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, content) {
            jQuery(content[0]).off('mousedown.axiom-selection');
            _this.removeAllHighlights(content[0]);
            var body = content.find('body');
            jQuery(body).removeClass('axiom-sel-in-action');
            if (_this.iframeHighlightBorders[index]) {
                _this.iframeHighlightBorders[index].eject();
            }
            try {
                var groupStyle_1 = content[0].getElementById('axiom-group-style');
                if (groupStyle_1) {
                    content[0].head.removeChild(groupStyle_1);
                }
                content.find('a').removeClass('axiom-link');
            }
            catch (e) {
                // If there's an error, don't worry be happy
            }
        });
        this.inuse = false;
        this.selectorData.selectors = [];
        this.matching = [];
        this.matchingData = [];
    };
    /**
     * Disables the usage of the tool
     */
    InjectedSelectorTool.prototype.ejectV0190 = function (doc) {
        this.ejectFromSpecificClasses();
        jQuery(document).off('mousedown.axiom-selection');
        jQuery('body').removeClass('axiom-sel-in-action');
        this.removeAllHighlights(doc);
        this.inuse = false;
        this.selectorData.selectors = [];
        this.matching = [];
        this.matchingData = [];
        var groupStyle = document.getElementById('axiom-group-style');
        if (groupStyle) {
            document.head.removeChild(groupStyle);
        }
        if (this.highlightBorder) {
            this.highlightBorder.eject();
        }
        jQuery('a').removeClass('axiom-link');
        jQuery('a').removeClass('axiom-download');
    };
    /**
     *
     */
    InjectedSelectorTool.prototype.resume = function (doc) {
        this.inuse = true;
        jQuery('body').addClass('axiom-sel-in-action');
        this.highlightBorder.setupBorder();
        // remove all selection as this is a brand new selection
        this.resetHighlights(doc);
    };
    /**
     * Remove all highlights
     */
    InjectedSelectorTool.prototype.resetHighlights = function (doc) {
        this.removeAllHighlights(doc);
        this.setHighlights(doc);
    };
    InjectedSelectorTool.prototype.setHighlights = function (doc) {
        var _this = this;
        // No point doing anything if Document is undefined, null or not a document at all; can happen rarely inside certain iframes
        if (!doc || !doc.getElementById) {
            return;
        }
        if (this.selectorData.selectors.length && this.selectionMode === 'multiple') {
            var selectors = this.selectorData.selectors.map(function (selectorObj) {
                if (!selectorObj.isToken && typeof selectorObj.selector === 'string' && selectorObj.selector !== 'head' && /\S/.test(selectorObj.selector)) {
                    return selectorObj.selector;
                }
                if (selectorObj.selector.hierarchy) {
                    return selectorObj.selector.hierarchy;
                }
            }).filter(function (s) { return !!s; });
            var combinedSelector = selectors.join(', ');
            var matches = [];
            if (typeof combinedSelector === 'string' && /\S/.test(combinedSelector)) {
                matches = Array.from(doc.querySelectorAll(combinedSelector));
            }
            var _loop_1 = function (s) {
                if (s === this_1.selectorData.activeSelectorIndex) {
                    for (var _a = 0, _b = this_1.selectorData.selectors[this_1.selectorData.activeSelectorIndex].selectedElements; _a < _b.length; _a++) {
                        var el = _b[_a];
                        if (el.classList)
                            el.classList.add(this_1.selectingClass + this_1.selectorData.activeSelectorIndex);
                    }
                    for (var _c = 0, _d = this_1.selectorData.selectors[this_1.selectorData.activeSelectorIndex].rejectedElements; _c < _d.length; _c++) {
                        var el = _d[_c];
                        if (el.classList)
                            el.classList.add(this_1.rejectingClass + this_1.selectorData.activeSelectorIndex);
                    }
                }
                if (selectors[s] && /\S/g.test(selectors[s])) {
                    var matchingEls = Array.from(doc.querySelectorAll(selectors[s])); // TODO: get combined selector from selectedEls
                    matchingEls.forEach(function (el) {
                        if (!/axiom-sel-selected-\S*|axiom-sel-rejected-\S*/g.test(el.className)) {
                            el.classList.add(_this.suggestingClass + s);
                        }
                    });
                }
            };
            var this_1 = this;
            for (var s = 0; s < selectors.length; s++) {
                _loop_1(s);
            }
            for (var _i = 0, matches_1 = matches; _i < matches_1.length; _i++) {
                var el = matches_1[_i];
                jQuery(el).addClass('axiom-matched');
                this.removeSelectedChildren(el);
            }
        }
        else if (this.selectionMode === 'single') {
            var sel = this.selectorData.selectors[0].selector;
            var el = void 0;
            if (sel.hierarchy) {
                el = document.querySelector(this.selectorData.selectors[0].selector.hierarchy);
            }
            else if (sel.innerText) {
                var xpath = "//*[text()='" + sel.innerText + "']";
                el = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            }
            jQuery(el).addClass('axiom-matched');
            jQuery(el).addClass('axiom-sel-selected-0');
        }
        var groupStyle = doc.getElementById('axiom-group-style');
        if (!groupStyle) {
            groupStyle = doc.createElement('style');
            groupStyle.id = 'axiom-group-style';
            doc.head.appendChild(groupStyle);
        }
        if (this.scrapeHelper.groupSelector !== undefined && this.scrapeHelper.groupSelector !== '' && this.scrapeHelper.groupSelector !== 'body') {
            groupStyle.innerHTML = this.scrapeHelper.groupSelector + " {\n                border-style: dotted !important;\n                border-width: 3px !important;\n                border-color: #FFC107 !important;\n                padding: 5px !important;\n                border-radius: 10px !important;\n            }";
        }
        else {
            groupStyle.innerHTML = '';
        }
        var otherSelectors = "\n        [class*=\"".concat(this.selectingClass, "\"].axiom-matched  {\n            background: rgba(0, 153, 255, 0.7) !important\n            background-image: none !important;\n        }\n        [class*=\"").concat(this.suggestingClass, "\"].axiom-matched  {\n            background: rgba(0, 153, 255, 0.3) !important;\n            background-image: none !important;\n        }\n        \n        [class*=\"").concat(this.selectingClass, "\"]:not(.axiom-matched)  {\n            background: rgba(153, 153, 153, 0.7) !important\n            background-image: none !important;\n        }\n        [class*=\"").concat(this.suggestingClass, "\"]:not(.axiom-matched)  {\n            background: rgba(153, 153, 153, 0.3) !important;\n            background-image: none !important;\n        }");
        var activeSelector = "\n        [class~=\"".concat(this.selectingClass + this.selectorData.activeSelectorIndex, "\"].axiom-matched  {\n            background-color: #FFC107 !important;\n            background-image: none !important;\n        }\n        [class~=\"").concat(this.suggestingClass + this.selectorData.activeSelectorIndex, "\"].axiom-matched  {\n            background-color: #ffd98c !important; \n            background-image: none !important;\n        }\n        \n        [class~=\"").concat(this.selectingClass + this.selectorData.activeSelectorIndex, "\"]:not(.axiom-matched)  {\n            background-color: rgba(193,193,193, 0.7) !important;\n            background-image: none !important;\n        }\n        [class~=\"").concat(this.suggestingClass + this.selectorData.activeSelectorIndex, "\"]:not(.axiom-matched)  {\n            background-color: rgba(193,193,193, 0.3) !important; \n            background-image: none !important;\n        }");
        groupStyle.innerHTML += otherSelectors;
        groupStyle.innerHTML += activeSelector;
    };
    InjectedSelectorTool.prototype.getSelector = function (element) {
        return this.SelectorAlgorithm.getSelector(element);
    };
    /**
     * Sets "'axiom-sel-selected-' + number" for the selection that has been clicked
     *
     */
    InjectedSelectorTool.prototype.setClassForSelected = function (el) {
        el.classList.add(this.selectingClass + this.selectorData.activeSelectorIndex);
        return;
    };
    /**
     * Removes "'axiom-sel-selected-' + number" for the selection that has been clicked
     *
     */
    InjectedSelectorTool.prototype.removeClassForSelected = function (el) {
        el.classList.remove(this.selectingClass + this.selectorData.activeSelectorIndex);
        return;
    };
    InjectedSelectorTool.prototype.removeClassForRejected = function (el) {
        el.classList.remove(this.rejectingClass + this.selectorData.activeSelectorIndex);
        return;
    };
    /**
     * Sets "'axiom-sel-suggested-' + number" for active selector's candidate selections
     *
     */
    InjectedSelectorTool.prototype.setClassForSuggested = function () {
        var cls = this.suggestingClass + this.selectorData.activeSelectorIndex;
        this.matching.forEach(function (el) {
            if (!/axiom-sel-selected-\S*|axiom-sel-rejected-\S*/g.test(el.className)) {
                el.classList.add(cls);
            }
        });
        return;
    };
    /**
     * Removes all classes which are injected for the highlighting purposes
     */
    InjectedSelectorTool.prototype.removeAllHighlights = function (doc) {
        if (!this.selectorData.selectors || this.selectorData.selectors.length === 0) {
            return;
        }
        for (var s = 0; s < this.selectorData.selectors.length; s++) {
            jQuery(doc).find('*').removeClass("axiom-sel-selected-".concat(s));
            jQuery(doc).find('*').removeClass("axiom-sel-suggested-".concat(s));
            jQuery(doc).find('*').removeClass("axiom-sel-rejected-".concat(s));
            jQuery(doc).find('*').removeClass("axiom-matched");
        }
    };
    /**
     * Highlights the the current selectors
     */
    InjectedSelectorTool.prototype.highlightSelection = function () {
        var _this = this;
        if (this.selectionMode === 'multiple') {
            var sel = document.querySelectorAll(this.selectingClass + this.selectorData.activeSelectorIndex);
            var sug = document.querySelectorAll(this.suggestingClass + this.selectorData.activeSelectorIndex);
            var reg = document.querySelectorAll(this.rejectingClass + this.selectorData.activeSelectorIndex);
            sel.forEach(function (el) {
                el.classList.add(_this.selectingClass + _this.selectorData.activeSelectorIndex);
            });
            sug.forEach(function (el) {
                el.classList.add(_this.suggestingClass + _this.selectorData.activeSelectorIndex);
            });
            reg.forEach(function (el) {
                el.classList.add(_this.rejectingClass + _this.selectorData.activeSelectorIndex);
            });
        }
        else {
            var sel = document.querySelectorAll(this.selectingClass + this.selectorData.activeSelectorIndex);
            sel.forEach(function (el) {
                el.classList.add(_this.selectingClass + _this.selectorData.activeSelectorIndex);
                el.classList.add('axiom-matched');
            });
        }
    };
    InjectedSelectorTool.prototype.findMatchesV0190 = function (doc) {
        if (this.selectionMode === 'multiple') {
            var newData = [];
            this.matching = []; // TODO: Check what this is actually doing. It's never checked anywhere I can see, just set.
            var selectors = this.selectorData.selectors.filter(function (s) {
                return typeof s.selector === 'string';
            }).map(function (s) {
                if (s.isToken) {
                    return "head";
                }
                else {
                    return s.selector;
                }
            });
            if (selectors.length) {
                if (this.resultTypes[0] === 'axiom-download' && selectors) {
                    try {
                        newData = Array.from(doc.querySelectorAll(selectors[0])).map(function (el) { return [el.outerHTML]; });
                    }
                    catch (e) {
                        // no action required
                    }
                }
                else {
                    newData = this.scrapeHelper.getPreview(doc, selectors, this.selectorData.selectors.map(function (s) { return s.resultType; }));
                }
            }
            newData = AxiomApiHelper_1.AxiomApiHelper.transpose(newData);
            if (newData.length > 0) {
                for (var n in newData) {
                    var skip = false;
                    if (newData[n] && newData[n].length > 0) {
                        for (var _i = 0, _a = newData[n]; _i < _a.length; _i++) {
                            var d = _a[_i];
                            if (d === "NO MATCHING ELEMENT") {
                                skip = true;
                                break;
                            }
                        }
                    }
                    if (!skip) {
                        this.matchingData[n] = newData[n];
                    }
                }
            }
            // Fix any holes in the data
            if (selectors.length > 1) {
                // First, determine the max number of columns
                var maxCols = 0;
                for (var i = 0; i < this.matchingData.length; i++) {
                    if (this.matchingData[i] && maxCols < this.matchingData[i].length) {
                        maxCols = this.matchingData[i].length;
                    }
                }
                // Then fill in the gaps!
                for (var i = 0; i < selectors.length; i++) {
                    var thisLen = this.matchingData[i] ? this.matchingData[i].length : 0;
                    if (thisLen < maxCols) {
                        for (var j = thisLen; j < maxCols; j++) {
                            if (!this.matchingData[i]) {
                                this.matchingData[i] = [];
                            }
                            this.matchingData[i].push('');
                        }
                    }
                }
            }
            // Trim matching data to maximum selector length
            if (this.matchingData.length > selectors.length) {
                this.matchingData = this.matchingData.slice(0, selectors.length);
            }
            // For any tokens, just add the token name into the matching data.
            for (var s = 0; s < this.selectorData.selectors.length; s++) {
                var sel = this.selectorData.selectors[s];
                if (sel.isToken) {
                    this.matchingData[s][0] = sel.selector;
                }
            }
        }
    };
    InjectedSelectorTool.prototype.blockClicksOn = function (doc) {
        // Block the entire screen to prevent anything else from being clicked. Amazing this works really!
        try {
            var block_1 = jQuery('<div>').css('position', 'fixed').css('z-index', '9999999').
                css('width', '10000px').css('height', '10000px').
                css('top', 0).css('left', 0).css('background-color', '');
            doc.body.appendChild(block_1.get(0));
            setTimeout(function () {
                block_1.remove();
            }, 300);
        }
        catch (e) {
            // Discard the error so we don't interrupt functionality
        }
        return false;
    };
    /**
     * When the selection is performed some widgets may require to perform any UI operation. Those are done here
     *
     * @param widgetType The type of widget to determine what to do
     */
    InjectedSelectorTool.prototype.closingAction = function (widgetType) {
        return __awaiter(this, void 0, void 0, function () {
            var selectedElements, elem_1, regex, buttonLabel, axiomWorkspace;
            return __generator(this, function (_a) {
                if (!this.selectorData.selectors[this.selectorData.activeSelectorIndex]) {
                    return [2 /*return*/];
                }
                if (this.selectionMode === "single" && widgetType && widgetType === 'WidgetDriverClick') {
                    selectedElements = this.selectorData.selectors[0].selector.hierarchy;
                    elem_1 = jQuery(selectedElements);
                    if (!elem_1[0]) {
                        return [2 /*return*/];
                    }
                    regex = new RegExp(/\w*(create|send|submit)\w*/gi);
                    buttonLabel = elem_1.text() || elem_1.val();
                    if (!regex.test(buttonLabel)) {
                        axiomWorkspace = document.getElementById('axiom-bot-draw-1976253492');
                        axiomWorkspace.classList.add("axiom-static");
                        $.confirm({
                            title: 'Selection Made',
                            content: 'Do you want to click this element now?',
                            boxWidth: '448px',
                            useBootstrap: false,
                            // Custom width
                            // https://craftpip.github.io/jquery-confirm/#custom-width
                            buttons: {
                                confirm: function () {
                                    if (elem_1[0].tagName.toLowerCase() == 'svg') {
                                        elem_1 = elem_1.parent();
                                    }
                                    elem_1[0].click();
                                    window.focus();
                                    chrome.runtime.sendMessage({ action: "focus_selector_interface" });
                                },
                                cancel: function () {
                                    window.focus();
                                    chrome.runtime.sendMessage({ action: "focus_selector_interface" });
                                    return;
                                }
                            }
                        });
                    }
                }
                return [2 /*return*/];
            });
        });
    };
    /**
     * Click Handler for single element selections when the selector tool is in action
     *
     * @param e
     */
    InjectedSelectorTool.prototype.singleElementClickHandler = function (e) {
        return __awaiter(this, void 0, void 0, function () {
            var x, singleSelection;
            var _this = this;
            return __generator(this, function (_a) {
                x = e.target;
                if (!x.classList.contains('axiom-selector-ignore')) {
                    if (this.resultType === 'link') {
                        while (x.parentElement && !/\S/.test(this.scrapeHelper.getData(x, this.resultType))) {
                            x = x.parentElement;
                        }
                    }
                }
                this.blockClicksOn(document);
                AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, content) {
                    _this.blockClicksOn(content[0]);
                });
                if (this.selectorData.selectors[this.selectorData.activeSelectorIndex] === undefined) {
                    this.selectorData.selectors[this.selectorData.activeSelectorIndex] = {
                        selector: '',
                        selections: [],
                        selectedElements: [],
                        rejectedElements: [],
                    };
                }
                singleSelection = this.singleSelector.getSelector(x);
                this.selectorData.selectors[this.selectorData.activeSelectorIndex].selector = singleSelection;
                this.removeAllHighlights(document);
                AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, content) {
                    _this.removeAllHighlights(content[0]);
                });
                this.sendStateUpdate();
                if (!this.selectorData.selectors[this.selectorData.activeSelectorIndex].selectedElements) {
                    this.selectorData.selectors[this.selectorData.activeSelectorIndex].selectedElements = [];
                }
                this.selectorData.selectors[this.selectorData.activeSelectorIndex].selectedElements.push(x);
                this.setHighlights(document);
                AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, content) {
                    _this.setHighlights(content[0]);
                });
                // Reset the token flag - if you select something, it's no longer selected by a token
                this.selectorData.selectors[this.selectorData.activeSelectorIndex].isToken = undefined;
                try {
                    this.sendStateUpdate();
                }
                catch (e) {
                    console.warn('Unable to send back message to the chrome extension on single element selection');
                }
                return [2 /*return*/];
            });
        });
    };
    /**
     * Go down the tree and remove any children of this element that have previously been selected but are no longer
     * matched by anything - orphaned selectors essentially, which appear as grey blocks that cannot be clicked on inside
     * a valid, working selector
     * @param e An element to find the children of and remove any selectors
     */
    InjectedSelectorTool.prototype.removeSelectedChildren = function (e) {
        var children = e.children;
        for (var i = 0; i < children.length; i++) {
            var child = children[i];
            child.classList.remove(this.selectingClass + this.selectorData.activeSelectorIndex);
            this.removeSelectedChildren(child);
        }
    };
    /**
     * Hanldes click when the selector tool is in action
     *
     * @param e
     */
    InjectedSelectorTool.prototype.elementClickHandler = function (e) {
        return __awaiter(this, void 0, void 0, function () {
            var x, suggestedElements, combinedSelector_1;
            var _this = this;
            return __generator(this, function (_a) {
                x = e.target;
                if (this.resultType === 'link') {
                    while (x.parentElement && !/\S/.test(this.scrapeHelper.getDataV0210(x, this.resultType))) {
                        x = x.parentElement;
                    }
                }
                this.blockClicksOn(document);
                AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, content) {
                    _this.blockClicksOn(content[0]);
                });
                if (this.selectorData.selectors[this.selectorData.activeSelectorIndex] === undefined) {
                    this.selectorData.selectors[this.selectorData.activeSelectorIndex] = {
                        selector: '',
                        selections: [],
                        selectedElements: [],
                        rejectedElements: [],
                        resultType: this.selectorData.defaultResultType,
                    };
                }
                else {
                    this.selectorData.selectors[this.selectorData.activeSelectorIndex].isToken = false;
                }
                if (!/axiom-tool/g.test(x.className)) {
                    suggestedElements = [];
                    try {
                        if (this.selectionMode = 'multiple') {
                            suggestedElements = Array.from(document.querySelectorAll(this.selectorData.selectors[this.selectorData.activeSelectorIndex].selector));
                        }
                    }
                    catch (e) {
                        suggestedElements = [];
                    }
                    if (suggestedElements.includes(x)) {
                        // if element is manually selected by user
                        if (this.selectorData.selectors[this.selectorData.activeSelectorIndex].selectedElements.includes(x)) {
                            // unselect element
                            x.classList.remove(this.selectingClass + this.selectorData.activeSelectorIndex);
                            this.selectorData.selectors[this.selectorData.activeSelectorIndex].selectedElements = this.selectorData.selectors[this.selectorData.activeSelectorIndex].selectedElements.filter(function (el) {
                                return el !== x;
                            });
                            // if we have deselected all elements then we should automatically deselect all rejected elements:
                            if (this.selectorData.selectors[this.selectorData.activeSelectorIndex].selectedElements.length === 0) {
                                this.selectorData.selectors[this.selectorData.activeSelectorIndex].rejectedElements = [];
                            }
                        }
                        else { // element is only suggested by the selection
                            // exclude the element
                            if (!this.selectorData.selectors[this.selectorData.activeSelectorIndex].rejectedElements.includes(x)) {
                                x.classList.add(this.rejectingClass + this.selectorData.activeSelectorIndex);
                                this.selectorData.selectors[this.selectorData.activeSelectorIndex].rejectedElements.push(x);
                            }
                            else {
                                x.classList.remove(this.rejectingClass + this.selectorData.activeSelectorIndex);
                                this.selectorData.selectors[this.selectorData.activeSelectorIndex].rejectedElements = this.selectorData.selectors[this.selectorData.activeSelectorIndex].rejectedElements.filter(function (el) {
                                    return el !== x;
                                });
                            }
                        }
                    }
                    else { // element is not currently included in the selection
                        if (this.selectorData.selectors[this.selectorData.activeSelectorIndex].rejectedElements.includes(x)) {
                            // element has previously been manually excluded: remove from rejected list
                            x.classList.remove(this.rejectingClass + this.selectorData.activeSelectorIndex);
                            this.selectorData.selectors[this.selectorData.activeSelectorIndex].rejectedElements = this.selectorData.selectors[this.selectorData.activeSelectorIndex].rejectedElements.filter(function (el) {
                                return el !== x;
                            });
                            // If this hasn't been tagged as matched, immediately re-select it; this can happen in the case where you unselect a non-selected
                            // element, and this removes everything. The main way that happens is when editing selectors.
                            if (!x.classList.contains("axiom-matched")) {
                                x.classList.add(this.selectingClass + this.selectorData.activeSelectorIndex);
                                this.selectorData.selectors[this.selectorData.activeSelectorIndex].selectedElements.push(x);
                            }
                        }
                        else { // element is not rejected or suggested
                            // select element
                            x.classList.add(this.selectingClass + this.selectorData.activeSelectorIndex);
                            this.selectorData.selectors[this.selectorData.activeSelectorIndex].selectedElements.push(x);
                        }
                    }
                    combinedSelector_1 = this.hierarchyActions.getCombined(document, this.selectorData.selectors[this.selectorData.activeSelectorIndex].selectedElements, this.selectorData.selectors[this.selectorData.activeSelectorIndex].rejectedElements, 'selector');
                    if (document.querySelectorAll(combinedSelector_1).length > 0) {
                        this.selectorData.selectors[this.selectorData.activeSelectorIndex].selector = combinedSelector_1;
                    }
                    else {
                        AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, content) {
                            combinedSelector_1 = _this.hierarchyActions.getCombined(content[0], _this.selectorData.selectors[_this.selectorData.activeSelectorIndex].selectedElements, _this.selectorData.selectors[_this.selectorData.activeSelectorIndex].rejectedElements, 'selector');
                            if (content[0].querySelectorAll(combinedSelector_1).length > 0) {
                                _this.selectorData.selectors[_this.selectorData.activeSelectorIndex].selector = combinedSelector_1;
                            }
                        });
                    }
                    this.findMatchesV0190(document);
                    this.resetHighlights(document);
                    AxiomApiHelper_1.AxiomApiHelper.applyToIframes(function (index, doc) {
                        try {
                            _this.findMatchesV0190(doc[0]);
                            _this.resetHighlights(doc[0]);
                        }
                        catch (e) {
                            // Discard any errors that happen in iframes
                        }
                    });
                    // Reset the token flag - if you select something, it's no longer selected by a token
                    this.selectorData.selectors[this.selectorData.activeSelectorIndex].isToken = undefined;
                    this.sendStateUpdate(true);
                }
                return [2 /*return*/, false];
            });
        });
    };
    return InjectedSelectorTool;
}());
exports.InjectedSelectorTool = InjectedSelectorTool;
window['axiom_selector'] = new InjectedSelectorTool();


/***/ },

/***/ 34613
(__unused_webpack_module, exports) {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
/**
 * Fetches the parent of the element in a string format
 */
var ParentElementSelector = /** @class */ (function () {
    function ParentElementSelector() {
    }
    ParentElementSelector.prototype.getSelector = function (el) {
        el.classList.remove('selectorgadget_selected');
        return el.parentElement.outerHTML.replace(/\"/g, "\'");
    };
    return ParentElementSelector;
}());
exports["default"] = ParentElementSelector;


/***/ },

/***/ 35812
(__unused_webpack_module, exports) {

"use strict";
var __webpack_unused_export__;

__webpack_unused_export__ = ({ value: true });
exports.WidgetsNestable = __webpack_unused_export__ = void 0;
var WidgetNestable = /** @class */ (function () {
    function WidgetNestable(indent, outdent, middent, widgetShow) {
        if (middent === void 0) { middent = ''; }
        if (widgetShow === void 0) { widgetShow = 'all'; }
        this.indent = indent;
        this.middent = middent;
        this.outdent = outdent;
        this.widgetShow = widgetShow;
    }
    return WidgetNestable;
}());
var NestingData = /** @class */ (function () {
    function NestingData(indent, startingBlock, endingBlock, midBlock) {
        if (midBlock === void 0) { midBlock = false; }
        this.indent = indent;
        this.startingBlock = startingBlock;
        this.midBlock = midBlock;
        this.endingBlock = endingBlock;
        this.outputShow = false;
    }
    return NestingData;
}());
__webpack_unused_export__ = NestingData;
var WidgetsNestable = /** @class */ (function () {
    function WidgetsNestable() {
        this.list = [
            new WidgetNestable('WidgetBotCreate', 'WidgetBotComplete'),
            new WidgetNestable('TemplateUIBot', 'TemplateUIBot'),
            new WidgetNestable('WidgetIf', 'WidgetIfEnd', 'WidgetElse'),
            new WidgetNestable('WidgetTry', 'WidgetTryCatchEnd', 'WidgetCatch'),
            new WidgetNestable('TemplateIfStatememt', 'TemplateIfStatement'),
            new WidgetNestable('TemplateIfElse', 'TemplateIfElse'),
            new WidgetNestable('TemplateLoopThroughData', 'TemplateLoopThroughData'),
            new WidgetNestable('TemplateTryCatch', 'TemplateTryCatch')
        ];
    }
    WidgetsNestable.prototype.getWidgetList = function (widgets, windex) {
        for (var _i = 0, _a = this.list; _i < _a.length; _i++) {
            var wn = _a[_i];
            for (var i = windex - 1; i >= 0; i--) {
                if (wn.indent === widgets[i].machine_name) {
                    for (var j = windex; j < widgets.length; j++) {
                        if (wn.outdent === widgets[j].machine_name) {
                            return wn.widgetShow;
                        }
                    }
                }
            }
        }
        return 'all';
    };
    WidgetsNestable.prototype.getIndentWindex = function (widgets, windex, indent) {
        var wn = this.list.filter(function (item) {
            return item.indent === indent;
        });
        if (!wn || wn.length === 0) {
            return -1;
        }
        for (var i = windex; i >= 0; i--) {
            if (wn[0].indent === widgets[i].machine_name) {
                return i;
            }
        }
        return -1;
    };
    WidgetsNestable.prototype.isNestable = function (widget) {
        if (!widget) {
            return 0;
        }
        for (var _i = 0, _a = this.list; _i < _a.length; _i++) {
            var item = _a[_i];
            if (item.indent === widget.machine_name) {
                return 1;
            }
            else if (item.outdent === widget.machine_name) {
                return 2;
            }
            else if (item.middent === widget.machine_name) {
                return 3;
            }
        }
        return 0;
    };
    WidgetsNestable.prototype.buildNestingData = function (widgets) {
        var indents = [];
        var indent = 0;
        for (var windex in widgets) {
            var isNestable = this.isNestable(widgets[windex]);
            switch (isNestable) {
                case 0:
                    indents[windex] = new NestingData(indent, false, false);
                    break;
                case 1:
                    indents[windex] = new NestingData(indent, true, false);
                    indent++;
                    break;
                case 2:
                    indent--;
                    indents[windex] = new NestingData(indent, false, true);
                    break;
                case 3:
                    indents[windex] = new NestingData(indent, false, false, true);
            }
        }
        return indents;
    };
    WidgetsNestable.prototype.nullNestingData = function () {
        return new NestingData(0, false, false);
    };
    return WidgetsNestable;
}());
exports.WidgetsNestable = WidgetsNestable;


/***/ },

/***/ 36634
(__unused_webpack_module, exports) {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
/**
 * Fetches the inner text of an element in a string
 */
var InnerTextSelector = /** @class */ (function () {
    function InnerTextSelector() {
    }
    InnerTextSelector.prototype.getSelector = function (el) {
        var content = el.textContent.trim();
        if (content && content.length < 1000) {
            return content;
        }
        return '';
    };
    return InnerTextSelector;
}());
exports["default"] = InnerTextSelector;


/***/ },

/***/ 40575
(__unused_webpack_module, exports) {

"use strict";

var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
var RunningData = /** @class */ (function () {
    function RunningData() {
        this.states = [];
    }
    RunningData.prototype.store = function (skipEvent) {
        if (skipEvent === void 0) { skipEvent = false; }
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2 /*return*/, new Promise(function (resolve) {
                        chrome.runtime.sendMessage({ greeting: 'running_data_store', skipEvent: skipEvent }, function () {
                            resolve('');
                        });
                    })];
            });
        });
    };
    RunningData.prototype.load = function (fireEventTrigger) {
        if (fireEventTrigger === void 0) { fireEventTrigger = false; }
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                return [2 /*return*/, new Promise(function (resolve) {
                        chrome.runtime.sendMessage({ greeting: 'running_data_load', fireEventTrigger: fireEventTrigger }, function (states) {
                            if (Array.isArray(states)) {
                                _this.states = states;
                                _this.countStates();
                            }
                            resolve('');
                        });
                    })];
            });
        });
    };
    RunningData.prototype.loadState = function (id) {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                return [2 /*return*/, new Promise(function (resolve) {
                        chrome.runtime.sendMessage({ greeting: 'running_data_load_state', id: id }, function (res) {
                            if (Array.isArray(res.states)) {
                                _this.states = res.states;
                                _this.countStates();
                            }
                            resolve(res.state);
                        });
                    })];
            });
        });
    };
    RunningData.prototype.addState = function (id, state, cloud) {
        if (cloud === void 0) { cloud = false; }
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                return [2 /*return*/, new Promise(function (resolve) {
                        chrome.runtime.sendMessage({ greeting: 'running_data_add_state', id: id, state: state, cloud: cloud }, function (res) {
                            if (Array.isArray(res.states)) {
                                _this.states = res.states;
                                _this.countStates();
                            }
                            resolve(res.state);
                        });
                    })];
            });
        });
    };
    RunningData.prototype.clearState = function (id) {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                return [2 /*return*/, new Promise(function (resolve) {
                        chrome.runtime.sendMessage({ greeting: 'running_data_clear_state', id: id }, function (states) {
                            if (Array.isArray(states)) {
                                _this.states = states;
                                _this.countStates();
                            }
                            resolve('');
                        });
                    })];
            });
        });
    };
    RunningData.prototype.clearAllStates = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                return [2 /*return*/, new Promise(function (resolve) {
                        chrome.runtime.sendMessage({ greeting: 'running_data_clear_all_states' }, function (states) {
                            _this.states = states;
                            _this.countStates();
                            resolve('');
                        });
                    })];
            });
        });
    };
    RunningData.prototype.cloudStateCount = function () {
        return this.csc;
    };
    RunningData.prototype.countStates = function () {
        this.csc = 0;
        this.dsc = 0;
        for (var _i = 0, _a = this.states; _i < _a.length; _i++) {
            var s = _a[_i];
            if (s.cloud) {
                this.csc++;
            }
            else {
                this.dsc++;
            }
        }
    };
    return RunningData;
}());
exports["default"] = RunningData;


/***/ },

/***/ 41510
(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.BorderHighlight = void 0;
var ScrapeHelper_1 = __webpack_require__(11258);
var BorderHighlight = /** @class */ (function () {
    function BorderHighlight(doc, iframeElement, iframeSupportEnabled) {
        var _this = this;
        if (iframeElement === void 0) { iframeElement = false; }
        if (iframeSupportEnabled === void 0) { iframeSupportEnabled = false; }
        this.borderWidth = 5;
        this.borderPadding = 2;
        this.activeSelectorIndex = 0;
        this.resultType = 'textContent';
        this.scrapeHelper = new ScrapeHelper_1.ScrapeHelper();
        this.doc = doc;
        this.iframeElement = iframeElement;
        this.iframeSupportEnabled = iframeSupportEnabled;
        doc.onscroll = function (e) {
            jQuery(_this.borderElement).hide();
        };
    }
    BorderHighlight.prototype.updateactiveSelectorIndex = function (id) {
        this.activeSelectorIndex = id;
    };
    BorderHighlight.prototype.updateResultType = function (resultType) {
        this.resultType = (resultType === 'axiom-download' ? "outerHTML" : resultType);
    };
    BorderHighlight.prototype.updateWindex = function (windex) {
        this.windex = windex;
    };
    BorderHighlight.prototype.inject = function () {
        this.setupBorder();
        jQuery(this.doc).on('mouseover.axiom-selection', this.mouseoverHandler.bind(this));
        jQuery(this.doc).on('mouseout.axiom-selection:not(.axiom-shield-overlay)', this.mouseLeaveHandler.bind(this));
    };
    BorderHighlight.prototype.eject = function () {
        this.removeBorderFromDom();
        jQuery(this.doc).off('mouseover.axiom-selection');
        jQuery(this.doc).off('mouseout.axiom-selection');
    };
    BorderHighlight.prototype.setupBorder = function () {
        if (!this.borderElement) {
            var width_1 = this.borderWidth + 'px';
            var bottomHeight = this.borderWidth * 2 + 'px';
            this.shieldOverlay = jQuery("<div class=\"axiom-shield-overlay axiom-tool axiom-selector-ignore\"></div>");
            this.borderElement = jQuery("<div class=\"axiom-tool-highlight-border\"></div>").hide();
            this.bTop = jQuery('<div>').addClass('axiom-border-highlight').addClass('axiom-border-top').css('height', width_1);
            this.bLeft = jQuery('<div>').addClass('axiom-border-highlight').addClass('axiom-border-left').css('width', width_1);
            this.bBottom = jQuery('<div>').addClass('axiom-border-highlight').addClass('axiom-border-bottom').css('min-height', width_1).css('text-overflow', 'clip').css('font-family', 'Quicksand,sans-serif');
            $(this.bBottom).each(function (index, el) {
                el.style.setProperty('padding-left', width_1, 'important');
            });
            this.preview = jQuery("\n            <div id=\"axiom-preview-wrapper\"\n            style=\"\n            position:relative!important;\n            left:0!important;\n            display: flex!important;\n            justify-content: center!important;\n            padding: 0!important;\n            justify-content: start!important;\n            font-size:12px!important;\n            line-height:0px!important;\n            background-color;red!important;\n            background;red!important;\n            min-height:10px!important;\n            height:auto!important;\n            max-width:400px!important;\n            width: auto!important;\n            white-space:nowrap!important;\n            overflow:visible!important;\n            overflow-x: clip!important;\n            margin: 0!important;\n            float:none!important;\n            font-weight:bold!important;\n            box-sizing: initial!important;\n            top: 5px!important;\n            scrollbar-width: none!important;\n            \"\n            >\n              <p\n              ></p>\n            </div>"); //TODO: hide this
            this.bBottom.append(this.preview);
            this.bRight = jQuery('<div>').addClass('axiom-border-highlight').addClass('axiom-border-right').css('width', width_1);
            this.addBorderToDom();
        }
    };
    BorderHighlight.prototype.removeBorderFromDom = function () {
        if (this.borderElement) {
            this.borderElement.remove();
            this.bTop.remove();
            this.bRight.remove();
            this.bBottom.remove();
            this.bRight.remove();
        }
        this.borderElement = this.bTop = this.bRight = this.bBottom = this.bLeft = null;
    };
    BorderHighlight.prototype.addBorderToDom = function () {
        this.borderElement.append(this.shieldOverlay);
        this.borderElement.append(this.bTop);
        this.borderElement.append(this.bRight);
        this.borderElement.append(this.bBottom);
        this.borderElement.append(this.bLeft);
        try {
            this.doc.body.appendChild(this.borderElement.get(0));
        }
        catch (e) {
            // No worries if it doesn't work
        }
    };
    BorderHighlight.prototype.showBorder = function () {
        this.borderElement.show();
    };
    BorderHighlight.prototype.removeBorder = function () {
        if (this.borderElement) {
            this.borderElement.hide();
        }
    };
    BorderHighlight.prototype.makeBorders = function (targetElem) {
        var _this = this;
        if (targetElem.tagName === 'IFRAME') {
            return;
        }
        var element = jQuery(targetElem);
        var position = element.offset();
        var top = position.top - scrollY;
        var left = position.left;
        var width = element.outerWidth();
        var height = element.outerHeight();
        this.preview.show();
        this.bTop.css('width', (width + this.borderPadding * 2 + this.borderWidth * 2) + 'px')
            .css('top', (top - this.borderWidth - this.borderPadding) + 'px')
            .css('left', (left - this.borderPadding - this.borderWidth) + 'px');
        this.bRight.css('height', (height + this.borderPadding * 2) + 'px')
            .css('top', (top - this.borderPadding) + 'px')
            .css('left', (left + width + this.borderPadding) + 'px');
        this.bBottom.css('width', (width + this.borderPadding * 2 + this.borderWidth * 2 - 5) + 'px')
            .css('top', (top + height + this.borderPadding) + 'px')
            .css('left', (left - this.borderPadding - this.borderWidth) + 'px')
            .css('color', '#F5F5F5')
            .css('height', this.borderWidth * 4 + 'px');
        this.bLeft.css('height', (height + this.borderPadding * 2) + 'px')
            .css('top', (top - this.borderPadding) + 'px')
            .css('left', (left - this.borderPadding - this.borderWidth) + 'px');
        this.shieldOverlay.css('top', top + 'px') // used to prevent selection of invlaid elements (iframes)
            .css('left', left + 'px');
        if (targetElem.tagName.toLowerCase() === 'iframe') { // we expand the shield over the dissalowed elements
            this.shieldOverlay.css('width', width + 'px')
                .css('height', height + 'px');
            this.shieldOverlay.off("click");
            this.shieldOverlay.click(function (e) {
                _this.shieldOverlay.off("click");
                if (_this.windex !== undefined) {
                    var navigate = confirm("You have selected content within an iframe that can't currently be selected. Would you like to try to goto the url?\n(Current selections will be lost if you click 'OK')");
                    if (navigate) {
                        var currentURL = window.location.href;
                        var frameSrc = targetElem.src;
                        // add goto widget with frame src
                        chrome.runtime.sendMessage({
                            action: "change_url",
                            origin: currentURL,
                            target: frameSrc,
                            windex: _this.windex
                        });
                    }
                }
                else {
                    alert("Magic button cannot be placed here, as this is a window getting content from a different website. Please select another area of the page");
                }
            });
        }
        else {
            this.shieldOverlay.css('width', 0 + 'px')
                .css('height', 0 + 'px');
            this.shieldOverlay.off("click");
        }
        // Make a way to target clicks on these border elements to direct to the element beneath
        // TODO
        // modify the colors if we are removing a selection
        var removingSelection = $(targetElem).is(".axiom-sel-suggested-".concat(this.activeSelectorIndex, ", .axiom-sel-selected-").concat(this.activeSelectorIndex));
        if (removingSelection) {
            $(".axiom-border-highlight").each(function (index, el) {
                el.style.setProperty("background-color", "rgb(245, 58, 58)", "important");
            });
        }
        else {
            $(".axiom-border-highlight").each(function (index, el) {
                el.style.setProperty("background-color", "#FFAB00", "important");
            });
        }
        if (this.iframeElement && !this.iframeSupportEnabled) {
            this.preview.children('p').text('Enable iframe support');
        }
        else {
            var preview = this.scrapeHelper.getData(targetElem, this.resultType);
            if (this.resultType === 'textContent') {
                var text = targetElem['innerText'];
                if (text) {
                    preview = text;
                }
                else {
                    preview = '';
                }
            }
            preview = (preview) ? preview : '';
            preview = (preview.length > 25) ? preview.substr(0, 25) + '...' : preview;
            this.preview.children('p').text(preview);
        }
        this.showBorder();
    };
    /**
     * This is just debarring the chrome extension items, we can make this more cool
     *
     * @param element
     */
    BorderHighlight.prototype.selectable = function (element) {
        if (element.tagName.toLowerCase() === "body" || jQuery(element).hasClass('axiom-selector-ignore')) {
            return false;
        }
        return true;
    };
    BorderHighlight.prototype.mouseoverHandler = function (e) {
        var target = e.target;
        if (this.resultType === 'link') {
            while (target.parentElement && !/\S/.test(this.scrapeHelper.getData(target, this.resultType))) {
                target = target.parentElement;
            }
        }
        if (this.selectable(target) && e.target !== this.shieldOverlay.get(0)) {
            this.makeBorders(target);
        }
    };
    BorderHighlight.prototype.mouseLeaveHandler = function (e) {
        if (e.target === this.doc.body || e.target === this.doc.body.parentNode || e.relatedTarget === this.shieldOverlay.get(0)) {
            return false;
        }
        this.removeBorder();
        return false;
    };
    BorderHighlight.prototype.setIframeSupportEnabled = function (val) {
        this.iframeSupportEnabled = val;
    };
    return BorderHighlight;
}());
exports.BorderHighlight = BorderHighlight;


/***/ },

/***/ 68037
(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.SelectorFacade = void 0;
var ClassSelector_1 = __importDefault(__webpack_require__(21149));
var ElementSelector_1 = __importDefault(__webpack_require__(74685));
var HierarchySelector_1 = __importDefault(__webpack_require__(99066));
var IdSelector_1 = __importDefault(__webpack_require__(13442));
var InnerTextSelector_1 = __importDefault(__webpack_require__(36634));
var ParentElementSelector_1 = __importDefault(__webpack_require__(34613));
/**
 * When the simmer selector fails, uses the naive hierarchy selector as a fallback
 */
var SelectorFacade = /** @class */ (function () {
    function SelectorFacade(multiple) {
        if (multiple === void 0) { multiple = false; }
        this.multiple = multiple;
        this.classSelector = new ClassSelector_1.default();
        this.hierarchySelector = new HierarchySelector_1.default();
        this.elementSelector = new ElementSelector_1.default();
        this.innerTextSelector = new InnerTextSelector_1.default();
        this.parentElementSelector = new ParentElementSelector_1.default();
        this.idSelector = new IdSelector_1.default();
    }
    SelectorFacade.prototype.getSelector = function (element) {
        var selected = false;
        var classSelector = this.classSelector.getSelector(element);
        var hierarchySelector = this.hierarchySelector.getSelector(element);
        var elementSelector = this.elementSelector.getSelector(element);
        var innerTextSelector = this.innerTextSelector.getSelector(element);
        var parentElementSelector = this.parentElementSelector.getSelector(element);
        var idSelector = this.idSelector.getSelector(element);
        selected = this.generateAxiomSelector(hierarchySelector, elementSelector, parentElementSelector, innerTextSelector, classSelector, idSelector);
        return selected;
    };
    SelectorFacade.prototype.generateAxiomSelector = function (hierarchy, targetElement, targetParent, innerText, classSel, idSel) {
        var axSel = {
            hierarchy: hierarchy,
            targetElement: targetElement,
            targetParent: targetParent,
            innerText: innerText,
            class: classSel,
            id: idSel
        };
        return axSel;
    };
    return SelectorFacade;
}());
exports.SelectorFacade = SelectorFacade;


/***/ },

/***/ 72560
(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
// ESM COMPAT FLAG
__webpack_require__.r(__webpack_exports__);

// EXPORTS
__webpack_require__.d(__webpack_exports__, {
  DiffMatchPatch: () => (/* reexport */ DiffMatchPatch),
  DiffOperation: () => (/* reexport */ DiffOperation),
  PatchObject: () => (/* reexport */ PatchObject)
});

// NAMESPACE OBJECT: ./node_modules/diff-match-patch-typescript/dist/es/utils/math.js
var math_namespaceObject = {};
__webpack_require__.r(math_namespaceObject);
__webpack_require__.d(math_namespaceObject, {
  max: () => (max),
  min: () => (min)
});

;// ./node_modules/diff-match-patch-typescript/dist/es/constants/index.js
const NON_ALPHA_NUMERIC_REGEX = /[^a-zA-Z0-9]/;
const WHITESPACE_REGEX = /\s/;
const LINEBREAK_REGEX = /[\r\n]/;
const BLANKLINE_END_REGEX = /\n\r?\n$/;
const BLANKLINE_START_REGEX = /^\r?\n\r?\n/;

;// ./node_modules/diff-match-patch-typescript/dist/es/types/DiffOperation.js
var DiffOperation;
(function (DiffOperation) {
    DiffOperation[DiffOperation["DIFF_DELETE"] = -1] = "DIFF_DELETE";
    DiffOperation[DiffOperation["DIFF_INSERT"] = 1] = "DIFF_INSERT";
    DiffOperation[DiffOperation["DIFF_EQUAL"] = 0] = "DIFF_EQUAL";
})(DiffOperation || (DiffOperation = {}));

;// ./node_modules/diff-match-patch-typescript/dist/es/types/Diff.js


;// ./node_modules/diff-match-patch-typescript/dist/es/types/index.js





;// ./node_modules/diff-match-patch-typescript/dist/es/utils/math.js
function min(a, b) {
    return a < b ? a : b;
}
function max(a, b) {
    return a > b ? a : b;
}

;// ./node_modules/diff-match-patch-typescript/dist/es/utils/index.js

const math = math_namespaceObject;

;// ./node_modules/diff-match-patch-typescript/dist/es/core/PatchObject.js

class PatchObject {
    diffs = [];
    start1 = 0;
    start2 = 0;
    length1 = 0;
    length2 = 0;
    toString() {
        let coords1;
        let coords2;
        if (this.length1 === 0) {
            coords1 = this.start1 + ",0";
        }
        else if (this.length1 === 1) {
            coords1 = this.start1 + 1;
        }
        else {
            coords1 = (this.start1 + 1) + "," + this.length1;
        }
        if (this.length2 === 0) {
            coords2 = this.start2 + ",0";
        }
        else if (this.length2 === 1) {
            coords2 = this.start2 + 1;
        }
        else {
            coords2 = (this.start2 + 1) + "," + this.length2;
        }
        const text = ["@@ -" + coords1 + " +" + coords2 + " @@\n"];
        let op;
        for (let x = 0; x < this.diffs.length; x++) {
            switch (this.diffs[x][0]) {
                case DiffOperation.DIFF_INSERT:
                    op = "+";
                    break;
                case DiffOperation.DIFF_DELETE:
                    op = "-";
                    break;
                case DiffOperation.DIFF_EQUAL:
                    op = " ";
                    break;
            }
            text[x + 1] = op + encodeURI(this.diffs[x][1]) + "\n";
        }
        return text.join("").replace(/%20/g, " ");
    }
}

;// ./node_modules/diff-match-patch-typescript/dist/es/core/DiffMatchPatch.js




class DiffMatchPatch {
    diffTimeout = 1.0;
    diffEditCost = 4;
    matchThreshold = 0.5;
    matchDistance = 1000;
    patchDeleteThreshold = 0.5;
    patchMargin = 4;
    matchMaxBits = 32;
    diff_main(text1, text2, optChecklines, optDeadline) {
        if (typeof optDeadline === "undefined") {
            if (this.diffTimeout <= 0) {
                optDeadline = Number.MAX_VALUE;
            }
            else {
                optDeadline = Date.now() + this.diffTimeout * 1000;
            }
        }
        const deadline = optDeadline;
        if (text1 == null || text2 == null) {
            throw new Error("Null input. (diff_main)");
        }
        if (text1 === text2) {
            if (text1) {
                return [[DiffOperation.DIFF_EQUAL, text1]];
            }
            return [];
        }
        if (typeof optChecklines === "undefined") {
            optChecklines = true;
        }
        const checklines = optChecklines;
        let commonlength = this.diff_commonPrefix(text1, text2);
        const commonprefix = text1.substring(0, commonlength);
        text1 = text1.substring(commonlength);
        text2 = text2.substring(commonlength);
        commonlength = this.diff_commonSuffix(text1, text2);
        const commonsuffix = text1.substring(text1.length - commonlength);
        text1 = text1.substring(0, text1.length - commonlength);
        text2 = text2.substring(0, text2.length - commonlength);
        const diffs = this.diff_compute_(text1, text2, checklines, deadline);
        if (commonprefix) {
            diffs.unshift([DiffOperation.DIFF_EQUAL, commonprefix]);
        }
        if (commonsuffix) {
            diffs.push([DiffOperation.DIFF_EQUAL, commonsuffix]);
        }
        this.diff_cleanupMerge(diffs);
        return diffs;
    }
    diff_commonPrefix(text1, text2) {
        if (!text1 ||
            !text2 ||
            text1.charAt(0) !== text2.charAt(0)) {
            return 0;
        }
        let pointermin = 0;
        let pointermax = math.min(text1.length, text2.length);
        let pointermid = pointermax;
        let pointerstart = 0;
        while (pointermin < pointermid) {
            if (text1.substring(pointerstart, pointermid) ===
                text2.substring(pointerstart, pointermid)) {
                pointermin = pointermid;
                pointerstart = pointermin;
            }
            else {
                pointermax = pointermid;
            }
            pointermid = Math.floor((pointermax - pointermin) / 2 + pointermin);
        }
        return pointermid;
    }
    diff_commonSuffix(text1, text2) {
        if (!text1 ||
            !text2 ||
            text1.charAt(text1.length - 1) !== text2.charAt(text2.length - 1)) {
            return 0;
        }
        let pointermin = 0;
        let pointermax = math.min(text1.length, text2.length);
        let pointermid = pointermax;
        let pointerend = 0;
        while (pointermin < pointermid) {
            if (text1.substring(text1.length - pointermid, text1.length - pointerend) ===
                text2.substring(text2.length - pointermid, text2.length - pointerend)) {
                pointermin = pointermid;
                pointerend = pointermin;
            }
            else {
                pointermax = pointermid;
            }
            pointermid = Math.floor((pointermax - pointermin) / 2 + pointermin);
        }
        return pointermid;
    }
    diff_cleanupSemantic(diffs) {
        let changes = false;
        const equalities = [];
        let equalitiesLength = 0;
        let lastEquality = null;
        let pointer = 0;
        let lengthInsertions1 = 0;
        let lengthDeletions1 = 0;
        let lengthInsertions2 = 0;
        let lengthDeletions2 = 0;
        while (pointer < diffs.length) {
            if (diffs[pointer][0] === DiffOperation.DIFF_EQUAL) {
                equalities[equalitiesLength++] = pointer;
                lengthInsertions1 = lengthInsertions2;
                lengthDeletions1 = lengthDeletions2;
                lengthInsertions2 = 0;
                lengthDeletions2 = 0;
                lastEquality = diffs[pointer][1];
            }
            else {
                if (diffs[pointer][0] === DiffOperation.DIFF_INSERT) {
                    lengthInsertions2 += diffs[pointer][1].length;
                }
                else {
                    lengthDeletions2 += diffs[pointer][1].length;
                }
                if (lastEquality &&
                    (lastEquality.length <= math.max(lengthInsertions1, lengthDeletions1)) &&
                    (lastEquality.length <= math.max(lengthInsertions2, lengthDeletions2))) {
                    diffs.splice(equalities[equalitiesLength - 1], 0, [DiffOperation.DIFF_DELETE, lastEquality]);
                    diffs[equalities[equalitiesLength - 1] + 1][0] = DiffOperation.DIFF_INSERT;
                    equalitiesLength--;
                    equalitiesLength--;
                    pointer = equalitiesLength > 0 ? equalities[equalitiesLength - 1] : -1;
                    lengthInsertions1 = 0;
                    lengthDeletions1 = 0;
                    lengthInsertions2 = 0;
                    lengthDeletions2 = 0;
                    lastEquality = null;
                    changes = true;
                }
            }
            pointer++;
        }
        if (changes) {
            this.diff_cleanupMerge(diffs);
        }
        this.diff_cleanupSemanticLossless(diffs);
        pointer = 1;
        while (pointer < diffs.length) {
            if (diffs[pointer - 1][0] === DiffOperation.DIFF_DELETE &&
                diffs[pointer][0] === DiffOperation.DIFF_INSERT) {
                const deletion = diffs[pointer - 1][1];
                const insertion = diffs[pointer][1];
                const overlapLength1 = this.diff_commonOverlap_(deletion, insertion);
                const overlapLength2 = this.diff_commonOverlap_(insertion, deletion);
                if (overlapLength1 >= overlapLength2) {
                    if (overlapLength1 >= deletion.length / 2 ||
                        overlapLength1 >= insertion.length / 2) {
                        diffs.splice(pointer, 0, [DiffOperation.DIFF_EQUAL, insertion.substring(0, overlapLength1)]);
                        diffs[pointer - 1][1] = deletion.substring(0, deletion.length - overlapLength1);
                        diffs[pointer + 1][1] = insertion.substring(overlapLength1);
                        pointer++;
                    }
                }
                else {
                    if (overlapLength2 >= deletion.length / 2 ||
                        overlapLength2 >= insertion.length / 2) {
                        diffs.splice(pointer, 0, [DiffOperation.DIFF_EQUAL, deletion.substring(0, overlapLength2)]);
                        diffs[pointer - 1][0] = DiffOperation.DIFF_INSERT;
                        diffs[pointer - 1][1] = insertion.substring(0, insertion.length - overlapLength2);
                        diffs[pointer + 1][0] = DiffOperation.DIFF_DELETE;
                        diffs[pointer + 1][1] = deletion.substring(overlapLength2);
                        pointer++;
                    }
                }
                pointer++;
            }
            pointer++;
        }
    }
    diff_cleanupSemanticLossless(diffs) {
        let pointer = 1;
        while (pointer < diffs.length - 1) {
            if (diffs[pointer - 1][0] === DiffOperation.DIFF_EQUAL &&
                diffs[pointer + 1][0] === DiffOperation.DIFF_EQUAL) {
                let equality1 = diffs[pointer - 1][1];
                let edit = diffs[pointer][1];
                let equality2 = diffs[pointer + 1][1];
                const commonOffset = this.diff_commonSuffix(equality1, edit);
                if (commonOffset) {
                    const commonString = edit.substring(edit.length - commonOffset);
                    equality1 = equality1.substring(0, equality1.length - commonOffset);
                    edit = commonString + edit.substring(0, edit.length - commonOffset);
                    equality2 = commonString + equality2;
                }
                let bestEquality1 = equality1;
                let bestEdit = edit;
                let bestEquality2 = equality2;
                let bestScore = this.diff_cleanupSemanticScore_(equality1, edit)
                    + this.diff_cleanupSemanticScore_(edit, equality2);
                while (edit.charAt(0) === equality2.charAt(0)) {
                    equality1 += edit.charAt(0);
                    edit = edit.substring(1) + equality2.charAt(0);
                    equality2 = equality2.substring(1);
                    const score = this.diff_cleanupSemanticScore_(equality1, edit)
                        + this.diff_cleanupSemanticScore_(edit, equality2);
                    if (score >= bestScore) {
                        bestScore = score;
                        bestEquality1 = equality1;
                        bestEdit = edit;
                        bestEquality2 = equality2;
                    }
                }
                if (diffs[pointer - 1][1] !== bestEquality1) {
                    if (bestEquality1) {
                        diffs[pointer - 1][1] = bestEquality1;
                    }
                    else {
                        diffs.splice(pointer - 1, 1);
                        pointer--;
                    }
                    diffs[pointer][1] = bestEdit;
                    if (bestEquality2) {
                        diffs[pointer + 1][1] = bestEquality2;
                    }
                    else {
                        diffs.splice(pointer + 1, 1);
                        pointer--;
                    }
                }
            }
            pointer++;
        }
    }
    diff_cleanupEfficiency(diffs) {
        let changes = false;
        const equalities = [];
        let equalitiesLength = 0;
        let lastEquality = null;
        let pointer = 0;
        let preIns = false;
        let preDel = false;
        let postIns = false;
        let postDel = false;
        while (pointer < diffs.length) {
            if (diffs[pointer][0] === DiffOperation.DIFF_EQUAL) {
                if (diffs[pointer][1].length < this.diffEditCost &&
                    (postIns || postDel)) {
                    equalities[equalitiesLength++] = pointer;
                    preIns = postIns;
                    preDel = postDel;
                    lastEquality = diffs[pointer][1];
                }
                else {
                    equalitiesLength = 0;
                    lastEquality = null;
                }
                postIns = postDel = false;
            }
            else {
                if (diffs[pointer][0] === DiffOperation.DIFF_DELETE) {
                    postDel = true;
                }
                else {
                    postIns = true;
                }
                if (lastEquality &&
                    ((preIns && preDel && postIns && postDel) ||
                        ((lastEquality.length < this.diffEditCost / 2) &&
                            (Number(preIns) + Number(preDel) + Number(postIns) + Number(postDel)) === 3))) {
                    diffs.splice(equalities[equalitiesLength - 1], 0, [DiffOperation.DIFF_DELETE, lastEquality]);
                    diffs[equalities[equalitiesLength - 1] + 1][0] = DiffOperation.DIFF_INSERT;
                    equalitiesLength--;
                    lastEquality = null;
                    if (preIns && preDel) {
                        postIns = postDel = true;
                        equalitiesLength = 0;
                    }
                    else {
                        equalitiesLength--;
                        pointer = equalitiesLength > 0 ? equalities[equalitiesLength - 1] : -1;
                        postIns = postDel = false;
                    }
                    changes = true;
                }
            }
            pointer++;
        }
        if (changes) {
            this.diff_cleanupMerge(diffs);
        }
    }
    diff_cleanupMerge(diffs) {
        diffs.push([DiffOperation.DIFF_EQUAL, ""]);
        let pointer = 0;
        let countDelete = 0;
        let countInsert = 0;
        let textDelete = "";
        let textInsert = "";
        let commonlength;
        while (pointer < diffs.length) {
            switch (diffs[pointer][0]) {
                case DiffOperation.DIFF_INSERT:
                    countInsert++;
                    textInsert += diffs[pointer][1];
                    pointer++;
                    break;
                case DiffOperation.DIFF_DELETE:
                    countDelete++;
                    textDelete += diffs[pointer][1];
                    pointer++;
                    break;
                case DiffOperation.DIFF_EQUAL:
                    if (countDelete + countInsert > 1) {
                        if (countDelete !== 0 && countInsert !== 0) {
                            commonlength = this.diff_commonPrefix(textInsert, textDelete);
                            if (commonlength !== 0) {
                                if ((pointer - countDelete - countInsert) > 0 &&
                                    (diffs[pointer - countDelete - countInsert - 1][0]
                                        === DiffOperation.DIFF_EQUAL)) {
                                    diffs[pointer - countDelete - countInsert - 1][1]
                                        += textInsert.substring(0, commonlength);
                                }
                                else {
                                    diffs.splice(0, 0, [DiffOperation.DIFF_EQUAL, textInsert.substring(0, commonlength)]);
                                    pointer++;
                                }
                                textInsert = textInsert.substring(commonlength);
                                textDelete = textDelete.substring(commonlength);
                            }
                            commonlength = this.diff_commonSuffix(textInsert, textDelete);
                            if (commonlength !== 0) {
                                diffs[pointer][1] = textInsert.substring(textInsert.length
                                    - commonlength) + diffs[pointer][1];
                                textInsert = textInsert.substring(0, textInsert.length - commonlength);
                                textDelete = textDelete.substring(0, textDelete.length - commonlength);
                            }
                        }
                        pointer -= countDelete + countInsert;
                        diffs.splice(pointer, countDelete + countInsert);
                        if (textDelete.length) {
                            diffs.splice(pointer, 0, [DiffOperation.DIFF_DELETE, textDelete]);
                            pointer++;
                        }
                        if (textInsert.length) {
                            diffs.splice(pointer, 0, [DiffOperation.DIFF_INSERT, textInsert]);
                            pointer++;
                        }
                        pointer++;
                    }
                    else if (pointer !== 0 && diffs[pointer - 1][0] === DiffOperation.DIFF_EQUAL) {
                        diffs[pointer - 1][1] += diffs[pointer][1];
                        diffs.splice(pointer, 1);
                    }
                    else {
                        pointer++;
                    }
                    countInsert = 0;
                    countDelete = 0;
                    textDelete = "";
                    textInsert = "";
                    break;
            }
        }
        if (diffs[diffs.length - 1][1] === "") {
            diffs.pop();
        }
        let changes = false;
        pointer = 1;
        while (pointer < diffs.length - 1) {
            if (diffs[pointer - 1][0] === DiffOperation.DIFF_EQUAL &&
                diffs[pointer + 1][0] === DiffOperation.DIFF_EQUAL) {
                if (diffs[pointer][1].substring(diffs[pointer][1].length - diffs[pointer - 1][1].length)
                    === diffs[pointer - 1][1]) {
                    diffs[pointer][1] = diffs[pointer - 1][1]
                        + diffs[pointer][1].substring(0, diffs[pointer][1].length - diffs[pointer - 1][1].length);
                    diffs[pointer + 1][1] = diffs[pointer - 1][1] + diffs[pointer + 1][1];
                    diffs.splice(pointer - 1, 1);
                    changes = true;
                }
                else if (diffs[pointer][1].substring(0, diffs[pointer + 1][1].length)
                    === diffs[pointer + 1][1]) {
                    diffs[pointer - 1][1] += diffs[pointer + 1][1];
                    diffs[pointer][1] = diffs[pointer][1].substring(diffs[pointer + 1][1].length)
                        + diffs[pointer + 1][1];
                    diffs.splice(pointer + 1, 1);
                    changes = true;
                }
            }
            pointer++;
        }
        if (changes) {
            this.diff_cleanupMerge(diffs);
        }
    }
    diff_xIndex(diffs, loc) {
        let chars1 = 0;
        let chars2 = 0;
        let lastChars1 = 0;
        let lastChars2 = 0;
        let x;
        for (x = 0; x < diffs.length; x++) {
            if (diffs[x][0] !== DiffOperation.DIFF_INSERT) {
                chars1 += diffs[x][1].length;
            }
            if (diffs[x][0] !== DiffOperation.DIFF_DELETE) {
                chars2 += diffs[x][1].length;
            }
            if (chars1 > loc) {
                break;
            }
            lastChars1 = chars1;
            lastChars2 = chars2;
        }
        if (diffs.length !== x &&
            diffs[x][0] === DiffOperation.DIFF_DELETE) {
            return lastChars2;
        }
        return lastChars2 + (loc - lastChars1);
    }
    diff_prettyHtml(diffs) {
        const html = [];
        const patternAMP = /&/g;
        const patternLT = /</g;
        const patternGT = />/g;
        const patternPARA = /\n/g;
        for (let x = 0; x < diffs.length; x++) {
            const op = diffs[x][0];
            const data = diffs[x][1];
            const text = data.replace(patternAMP, "&amp;")
                .replace(patternLT, "&lt;")
                .replace(patternGT, "&gt;")
                .replace(patternPARA, "&para;<br>");
            switch (op) {
                case DiffOperation.DIFF_INSERT:
                    html[x] = '<ins style="background:#e6ffe6;">' + text + "</ins>";
                    break;
                case DiffOperation.DIFF_DELETE:
                    html[x] = '<del style="background:#ffe6e6;">' + text + "</del>";
                    break;
                case DiffOperation.DIFF_EQUAL:
                    html[x] = "<span>" + text + "</span>";
                    break;
            }
        }
        return html.join("");
    }
    diff_text1(diffs) {
        const text = [];
        for (let x = 0; x < diffs.length; x++) {
            if (diffs[x][0] !== DiffOperation.DIFF_INSERT) {
                text[x] = diffs[x][1];
            }
        }
        return text.join("");
    }
    diff_text2(diffs) {
        const text = [];
        for (let x = 0; x < diffs.length; x++) {
            if (diffs[x][0] !== DiffOperation.DIFF_DELETE) {
                text[x] = diffs[x][1];
            }
        }
        return text.join("");
    }
    diff_levenshtein(diffs) {
        let levenshtein = 0;
        let insertions = 0;
        let deletions = 0;
        for (let x = 0; x < diffs.length; x++) {
            const op = diffs[x][0];
            const data = diffs[x][1];
            switch (op) {
                case DiffOperation.DIFF_INSERT:
                    insertions += data.length;
                    break;
                case DiffOperation.DIFF_DELETE:
                    deletions += data.length;
                    break;
                case DiffOperation.DIFF_EQUAL:
                    levenshtein += math.max(insertions, deletions);
                    insertions = 0;
                    deletions = 0;
                    break;
            }
        }
        levenshtein += math.max(insertions, deletions);
        return levenshtein;
    }
    diff_toDelta(diffs) {
        const text = [];
        for (let x = 0; x < diffs.length; x++) {
            switch (diffs[x][0]) {
                case DiffOperation.DIFF_INSERT:
                    text[x] = "+" + encodeURI(diffs[x][1]);
                    break;
                case DiffOperation.DIFF_DELETE:
                    text[x] = "-" + diffs[x][1].length;
                    break;
                case DiffOperation.DIFF_EQUAL:
                    text[x] = "=" + diffs[x][1].length;
                    break;
            }
        }
        return text.join("\t").replace(/%20/g, " ");
    }
    diff_fromDelta(text1, delta) {
        const diffs = [];
        let diffsLength = 0;
        let pointer = 0;
        const tokens = delta.split(/\t/g);
        for (let x = 0; x < tokens.length; x++) {
            const param = tokens[x].substring(1);
            switch (tokens[x].charAt(0)) {
                case "+":
                    try {
                        diffs[diffsLength++] = [DiffOperation.DIFF_INSERT, decodeURI(param)];
                    }
                    catch {
                        throw new Error("Illegal escape in diff_fromDelta: " + param);
                    }
                    break;
                case "-":
                case "=":
                    const n = parseInt(param, 10);
                    if (isNaN(n) || n < 0) {
                        throw new Error("Invalid number in diff_fromDelta: " + param);
                    }
                    const text = text1.substring(pointer, pointer += n);
                    if (tokens[x].charAt(0) === "=") {
                        diffs[diffsLength++] = [DiffOperation.DIFF_EQUAL, text];
                    }
                    else {
                        diffs[diffsLength++] = [DiffOperation.DIFF_DELETE, text];
                    }
                    break;
                default:
                    if (tokens[x]) {
                        throw new Error("Invalid diff operation in diff_fromDelta: " + tokens[x]);
                    }
            }
        }
        if (pointer !== text1.length) {
            throw new Error("Delta length (" + pointer + ") does not equal source text length ("
                + text1.length + ")");
        }
        return diffs;
    }
    diff_linesToChars(text1, text2) {
        const lineArray = [];
        const lineHash = {};
        lineArray[0] = "";
        const chars1 = this.diff_linesToCharsMunge_(text1, lineArray, lineHash, 40000);
        const chars2 = this.diff_linesToCharsMunge_(text2, lineArray, lineHash, 65535);
        return { chars1, chars2, lineArray };
    }
    diff_charsToLines(diffs, lineArray) {
        for (let i = 0; i < diffs.length; i++) {
            const chars = diffs[i][1];
            const text = [];
            for (let j = 0; j < chars.length; j++) {
                text[j] = lineArray[chars.charCodeAt(j)];
            }
            diffs[i][1] = text.join("");
        }
    }
    match_main(text, pattern, loc) {
        if (text == null || pattern == null || loc == null) {
            throw new Error("Null input. (match_main)");
        }
        loc = math.max(0, math.min(loc, text.length));
        if (text === pattern) {
            return 0;
        }
        else if (!text.length) {
            return -1;
        }
        else if (text.substring(loc, loc + pattern.length) === pattern) {
            return loc;
        }
        else {
            return this.match_bitap_(text, pattern, loc);
        }
    }
    patch_make(a, optB, optC) {
        let text1;
        let diffs;
        if (typeof a === "string" &&
            typeof optB === "string" &&
            typeof optC === "undefined") {
            text1 = a;
            diffs = this.diff_main(text1, optB, true);
            if (diffs.length > 2) {
                this.diff_cleanupSemantic(diffs);
                this.diff_cleanupEfficiency(diffs);
            }
        }
        else if (a &&
            typeof a === "object" &&
            typeof optB === "undefined" &&
            typeof optC === "undefined") {
            diffs = a;
            text1 = this.diff_text1(diffs);
        }
        else if (typeof a === "string" &&
            optB &&
            typeof optB === "object" &&
            typeof optC === "undefined") {
            text1 = a;
            diffs = optB;
        }
        else if (typeof a === "string" &&
            typeof optB === "string" &&
            optC &&
            typeof optC === "object") {
            text1 = a;
            diffs = optC;
        }
        else {
            throw new Error("Unknown call format to patch_make");
        }
        if (diffs.length === 0) {
            return [];
        }
        const patches = [];
        let patch = new PatchObject();
        let patchDiffLength = 0;
        let charCount1 = 0;
        let charCount2 = 0;
        let prepatchText = text1;
        let postpatchText = text1;
        for (let x = 0; x < diffs.length; x++) {
            const diffType = diffs[x][0];
            const diffText = diffs[x][1];
            if (!patchDiffLength && diffType !== DiffOperation.DIFF_EQUAL) {
                patch.start1 = charCount1;
                patch.start2 = charCount2;
            }
            switch (diffType) {
                case DiffOperation.DIFF_INSERT:
                    patch.diffs[patchDiffLength++] = diffs[x];
                    patch.length2 += diffText.length;
                    postpatchText = postpatchText.substring(0, charCount2)
                        + diffText + postpatchText.substring(charCount2);
                    break;
                case DiffOperation.DIFF_DELETE:
                    patch.length1 += diffText.length;
                    patch.diffs[patchDiffLength++] = diffs[x];
                    postpatchText = postpatchText.substring(0, charCount2)
                        + postpatchText.substring(charCount2 + diffText.length);
                    break;
                case DiffOperation.DIFF_EQUAL:
                    if (diffText.length <= 2 * this.patchMargin &&
                        patchDiffLength &&
                        diffs.length !== x + 1) {
                        patch.diffs[patchDiffLength++] = diffs[x];
                        patch.length1 += diffText.length;
                        patch.length2 += diffText.length;
                    }
                    else if (diffText.length >= 2 * this.patchMargin) {
                        if (patchDiffLength) {
                            this.patch_addContext_(patch, prepatchText);
                            patches.push(patch);
                            patch = new PatchObject();
                            patchDiffLength = 0;
                            prepatchText = postpatchText;
                            charCount1 = charCount2;
                        }
                    }
                    break;
            }
            if (diffType !== DiffOperation.DIFF_INSERT) {
                charCount1 += diffText.length;
            }
            if (diffType !== DiffOperation.DIFF_DELETE) {
                charCount2 += diffText.length;
            }
        }
        if (patchDiffLength) {
            this.patch_addContext_(patch, prepatchText);
            patches.push(patch);
        }
        return patches;
    }
    patch_deepCopy(patches) {
        const patchesCopy = [];
        for (let x = 0; x < patches.length; x++) {
            const patch = patches[x];
            const patchCopy = new PatchObject();
            for (let y = 0; y < patch.diffs.length; y++) {
                patchCopy.diffs[y] = [patch.diffs[y][0], patch.diffs[y][1]];
            }
            patchCopy.start1 = patch.start1;
            patchCopy.start2 = patch.start2;
            patchCopy.length1 = patch.length1;
            patchCopy.length2 = patch.length2;
            patchesCopy[x] = patchCopy;
        }
        return patchesCopy;
    }
    patch_apply(patches, text) {
        if (patches.length === 0) {
            return [text, []];
        }
        patches = this.patch_deepCopy(patches);
        const nullPadding = this.patch_addPadding(patches);
        text = nullPadding + text + nullPadding;
        this.patch_splitMax(patches);
        let delta = 0;
        const results = [];
        for (let x = 0; x < patches.length; x++) {
            const expectedLoc = patches[x].start2 + delta;
            const text1 = this.diff_text1(patches[x].diffs);
            let startLoc;
            let endLoc = -1;
            if (text1.length > this.matchMaxBits) {
                startLoc = this.match_main(text, text1.substring(0, this.matchMaxBits), expectedLoc);
                if (startLoc !== -1) {
                    endLoc = this.match_main(text, text1.substring(text1.length - this.matchMaxBits), expectedLoc + text1.length - this.matchMaxBits);
                    if (endLoc === -1 || startLoc >= endLoc) {
                        startLoc = -1;
                    }
                }
            }
            else {
                startLoc = this.match_main(text, text1, expectedLoc);
            }
            if (startLoc === -1) {
                results[x] = false;
                delta -= patches[x].length2 - patches[x].length1;
            }
            else {
                results[x] = true;
                delta = startLoc - expectedLoc;
                let text2;
                if (endLoc === -1) {
                    text2 = text.substring(startLoc, startLoc + text1.length);
                }
                else {
                    text2 = text.substring(startLoc, endLoc + this.matchMaxBits);
                }
                if (text1 === text2) {
                    text = text.substring(0, startLoc)
                        + this.diff_text2(patches[x].diffs)
                        + text.substring(startLoc + text1.length);
                }
                else {
                    const diffs = this.diff_main(text1, text2, false);
                    if (text1.length > this.matchMaxBits &&
                        this.diff_levenshtein(diffs) / text1.length > this.patchDeleteThreshold) {
                        results[x] = false;
                    }
                    else {
                        this.diff_cleanupSemanticLossless(diffs);
                        let index1 = 0;
                        let index2 = 0;
                        for (let y = 0; y < patches[x].diffs.length; y++) {
                            const mod = patches[x].diffs[y];
                            if (mod[0] !== DiffOperation.DIFF_EQUAL) {
                                index2 = this.diff_xIndex(diffs, index1);
                            }
                            if (mod[0] === DiffOperation.DIFF_INSERT) {
                                text = text.substring(0, startLoc + index2) + mod[1]
                                    + text.substring(startLoc + index2);
                            }
                            else if (mod[0] === DiffOperation.DIFF_DELETE) {
                                text = text.substring(0, startLoc + index2)
                                    + text.substring(startLoc
                                        + this.diff_xIndex(diffs, index1 + mod[1].length));
                            }
                            if (mod[0] !== DiffOperation.DIFF_DELETE) {
                                index1 += mod[1].length;
                            }
                        }
                    }
                }
            }
        }
        text = text.substring(nullPadding.length, text.length - nullPadding.length);
        return [text, results];
    }
    patch_addPadding(patches) {
        const paddingLength = this.patchMargin;
        let nullPadding = "";
        for (let x = 1; x <= paddingLength; x++) {
            nullPadding += String.fromCharCode(x);
        }
        for (let x = 0; x < patches.length; x++) {
            patches[x].start1 += paddingLength;
            patches[x].start2 += paddingLength;
        }
        let patch = patches[0];
        let diffs = patch.diffs;
        if (diffs.length === 0 || diffs[0][0] !== DiffOperation.DIFF_EQUAL) {
            diffs.unshift([DiffOperation.DIFF_EQUAL, nullPadding]);
            patch.start1 -= paddingLength;
            patch.start2 -= paddingLength;
            patch.length1 += paddingLength;
            patch.length2 += paddingLength;
        }
        else if (paddingLength > diffs[0][1].length) {
            const extraLength = paddingLength - diffs[0][1].length;
            diffs[0][1] = nullPadding.substring(diffs[0][1].length) + diffs[0][1];
            patch.start1 -= extraLength;
            patch.start2 -= extraLength;
            patch.length1 += extraLength;
            patch.length2 += extraLength;
        }
        patch = patches[patches.length - 1];
        diffs = patch.diffs;
        if (diffs.length === 0 || diffs[diffs.length - 1][0] !== DiffOperation.DIFF_EQUAL) {
            diffs.push([DiffOperation.DIFF_EQUAL, nullPadding]);
            patch.length1 += paddingLength;
            patch.length2 += paddingLength;
        }
        else if (paddingLength > diffs[diffs.length - 1][1].length) {
            const extraLength = paddingLength - diffs[diffs.length - 1][1].length;
            diffs[diffs.length - 1][1] += nullPadding.substring(0, extraLength);
            patch.length1 += extraLength;
            patch.length2 += extraLength;
        }
        return nullPadding;
    }
    patch_splitMax(patches) {
        const patchSize = this.matchMaxBits;
        for (let x = 0; x < patches.length; x++) {
            if (patches[x].length1 <= patchSize) {
                continue;
            }
            const bigpatch = patches[x];
            patches.splice(x--, 1);
            let start1 = bigpatch.start1;
            let start2 = bigpatch.start2;
            let precontext = "";
            while (bigpatch.diffs.length !== 0) {
                const patch = new PatchObject();
                let empty = true;
                patch.start1 = start1 - precontext.length;
                patch.start2 = start2 - precontext.length;
                if (precontext !== "") {
                    patch.length1 = patch.length2 = precontext.length;
                    patch.diffs.push([DiffOperation.DIFF_EQUAL, precontext]);
                }
                while (bigpatch.diffs.length !== 0 &&
                    patch.length1 < patchSize - this.patchMargin) {
                    const diffType = bigpatch.diffs[0][0];
                    let diffText = bigpatch.diffs[0][1];
                    if (diffType === DiffOperation.DIFF_INSERT) {
                        patch.length2 += diffText.length;
                        start2 += diffText.length;
                        patch.diffs.push(bigpatch.diffs.shift());
                        empty = false;
                    }
                    else if (diffType === DiffOperation.DIFF_DELETE &&
                        patch.diffs.length === 1 &&
                        patch.diffs[0][0] === DiffOperation.DIFF_EQUAL &&
                        diffText.length > 2 * patchSize) {
                        patch.length1 += diffText.length;
                        start1 += diffText.length;
                        empty = false;
                        patch.diffs.push([diffType, diffText]);
                        bigpatch.diffs.shift();
                    }
                    else {
                        diffText = diffText.substring(0, patchSize - patch.length1 - this.patchMargin);
                        patch.length1 += diffText.length;
                        start1 += diffText.length;
                        if (diffType === DiffOperation.DIFF_EQUAL) {
                            patch.length2 += diffText.length;
                            start2 += diffText.length;
                        }
                        else {
                            empty = false;
                        }
                        patch.diffs.push([diffType, diffText]);
                        if (diffText === bigpatch.diffs[0][1]) {
                            bigpatch.diffs.shift();
                        }
                        else {
                            bigpatch.diffs[0][1] = bigpatch.diffs[0][1].substring(diffText.length);
                        }
                    }
                }
                precontext = this.diff_text2(patch.diffs);
                precontext = precontext.substring(precontext.length - this.patchMargin);
                const postcontext = this.diff_text1(bigpatch.diffs).substring(0, this.patchMargin);
                if (postcontext !== "") {
                    patch.length1 += postcontext.length;
                    patch.length2 += postcontext.length;
                    if (patch.diffs.length !== 0 &&
                        patch.diffs[patch.diffs.length - 1][0] === DiffOperation.DIFF_EQUAL) {
                        patch.diffs[patch.diffs.length - 1][1] += postcontext;
                    }
                    else {
                        patch.diffs.push([DiffOperation.DIFF_EQUAL, postcontext]);
                    }
                }
                if (!empty) {
                    patches.splice(++x, 0, patch);
                }
            }
        }
    }
    patch_toText(patches) {
        const text = [];
        for (let x = 0; x < patches.length; x++) {
            text[x] = patches[x];
        }
        return text.join("");
    }
    patch_fromText(textline) {
        const patches = [];
        if (!textline) {
            return patches;
        }
        const text = textline.split("\n");
        let textPointer = 0;
        const patchHeader = /^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@$/;
        while (textPointer < text.length) {
            const m = text[textPointer].match(patchHeader);
            if (!m) {
                throw new Error("Invalid patch string: " + text[textPointer]);
            }
            const patch = new PatchObject();
            patches.push(patch);
            patch.start1 = parseInt(m[1], 10);
            if (m[2] === "") {
                patch.start1--;
                patch.length1 = 1;
            }
            else if (m[2] === "0") {
                patch.length1 = 0;
            }
            else {
                patch.start1--;
                patch.length1 = parseInt(m[2], 10);
            }
            patch.start2 = parseInt(m[3], 10);
            if (m[4] === "") {
                patch.start2--;
                patch.length2 = 1;
            }
            else if (m[4] === "0") {
                patch.length2 = 0;
            }
            else {
                patch.start2--;
                patch.length2 = parseInt(m[4], 10);
            }
            textPointer++;
            let sign;
            let line;
            let rawLine;
            while (textPointer < text.length) {
                sign = text[textPointer].charAt(0);
                rawLine = text[textPointer].substring(1);
                try {
                    line = decodeURI(rawLine);
                }
                catch {
                    throw new Error("Illegal escape in patch_fromText: " + rawLine);
                }
                if (sign === "-") {
                    patch.diffs.push([DiffOperation.DIFF_DELETE, line]);
                }
                else if (sign === "+") {
                    patch.diffs.push([DiffOperation.DIFF_INSERT, line]);
                }
                else if (sign === " ") {
                    patch.diffs.push([DiffOperation.DIFF_EQUAL, line]);
                }
                else if (sign === "@") {
                    break;
                }
                else if (sign === "") {
                }
                else {
                    throw new Error('Invalid patch mode "' + sign + '" in: ' + line);
                }
                textPointer++;
            }
        }
        return patches;
    }
    diff_compute_(text1, text2, checklines, deadline) {
        let diffs;
        if (!text1) {
            return [[DiffOperation.DIFF_INSERT, text2]];
        }
        if (!text2) {
            return [[DiffOperation.DIFF_DELETE, text1]];
        }
        const longtext = text1.length > text2.length ? text1 : text2;
        const shorttext = text1.length > text2.length ? text2 : text1;
        const i = longtext.indexOf(shorttext);
        if (i !== -1) {
            diffs = [
                [DiffOperation.DIFF_INSERT, longtext.substring(0, i)],
                [DiffOperation.DIFF_EQUAL, shorttext],
                [DiffOperation.DIFF_INSERT, longtext.substring(i + shorttext.length)]
            ];
            if (text1.length > text2.length) {
                diffs[0][0] = DiffOperation.DIFF_DELETE;
                diffs[2][0] = DiffOperation.DIFF_DELETE;
            }
            return diffs;
        }
        if (shorttext.length === 1) {
            return [
                [DiffOperation.DIFF_DELETE, text1],
                [DiffOperation.DIFF_INSERT, text2]
            ];
        }
        const hm = this.diff_halfMatch_(text1, text2);
        if (hm) {
            const text1A = hm[0];
            const text1B = hm[1];
            const text2A = hm[2];
            const text2B = hm[3];
            const midCommon = hm[4];
            const diffsA = this.diff_main(text1A, text2A, checklines, deadline);
            const diffsB = this.diff_main(text1B, text2B, checklines, deadline);
            return diffsA.concat([[DiffOperation.DIFF_EQUAL, midCommon]], diffsB);
        }
        if (checklines && text1.length > 100 && text2.length > 100) {
            return this.diff_lineMode_(text1, text2, deadline);
        }
        return this.diff_bisect_(text1, text2, deadline);
    }
    diff_lineMode_(text1, text2, deadline) {
        const a = this.diff_linesToChars(text1, text2);
        text1 = a.chars1;
        text2 = a.chars2;
        const linearray = a.lineArray;
        const diffs = this.diff_main(text1, text2, false, deadline);
        this.diff_charsToLines(diffs, linearray);
        this.diff_cleanupSemantic(diffs);
        diffs.push([DiffOperation.DIFF_EQUAL, ""]);
        let pointer = 0;
        let countDelete = 0;
        let countInsert = 0;
        let textDelete = "";
        let textInsert = "";
        while (pointer < diffs.length) {
            switch (diffs[pointer][0]) {
                case DiffOperation.DIFF_INSERT:
                    countInsert++;
                    textInsert += diffs[pointer][1];
                    break;
                case DiffOperation.DIFF_DELETE:
                    countDelete++;
                    textDelete += diffs[pointer][1];
                    break;
                case DiffOperation.DIFF_EQUAL:
                    if (countDelete >= 1 && countInsert >= 1) {
                        diffs.splice(pointer - countDelete - countInsert, countDelete + countInsert);
                        pointer = pointer - countDelete - countInsert;
                        const subDiff = this.diff_main(textDelete, textInsert, false, deadline);
                        for (let j = subDiff.length - 1; j >= 0; j--) {
                            diffs.splice(pointer, 0, subDiff[j]);
                        }
                        pointer = pointer + subDiff.length;
                    }
                    countInsert = 0;
                    countDelete = 0;
                    textDelete = "";
                    textInsert = "";
                    break;
            }
            pointer++;
        }
        diffs.pop();
        return diffs;
    }
    diff_bisect_(text1, text2, deadline) {
        const text1Length = text1.length;
        const text2Length = text2.length;
        const maxD = Math.ceil((text1Length + text2Length) / 2);
        const vOffset = maxD;
        const vLength = 2 * maxD;
        const v1 = new Array(vLength);
        const v2 = new Array(vLength);
        for (let x = 0; x < vLength; x++) {
            v1[x] = -1;
            v2[x] = -1;
        }
        v1[vOffset + 1] = 0;
        v2[vOffset + 1] = 0;
        const delta = text1Length - text2Length;
        const front = (delta % 2 !== 0);
        let k1Start = 0;
        let k1End = 0;
        let k2Start = 0;
        let k2End = 0;
        for (let d = 0; d < maxD; d++) {
            if (Date.now() > deadline) {
                break;
            }
            for (let k1 = -d + k1Start; k1 <= d - k1End; k1 += 2) {
                const k1Offset = vOffset + k1;
                let x1;
                if (k1 === -d || (k1 !== d && v1[k1Offset - 1] < v1[k1Offset + 1])) {
                    x1 = v1[k1Offset + 1];
                }
                else {
                    x1 = v1[k1Offset - 1] + 1;
                }
                let y1 = x1 - k1;
                while (x1 < text1Length
                    && y1 < text2Length
                    && text1.charAt(x1) === text2.charAt(y1)) {
                    x1++;
                    y1++;
                }
                v1[k1Offset] = x1;
                if (x1 > text1Length) {
                    k1End += 2;
                }
                else if (y1 > text2Length) {
                    k1Start += 2;
                }
                else if (front) {
                    const k2Offset = vOffset + delta - k1;
                    if (k2Offset >= 0 && k2Offset < vLength && v2[k2Offset] !== -1) {
                        const x2 = text1Length - v2[k2Offset];
                        if (x1 >= x2) {
                            return this.diff_bisectSplit_(text1, text2, x1, y1, deadline);
                        }
                    }
                }
            }
            for (let k2 = -d + k2Start; k2 <= d - k2End; k2 += 2) {
                const k2Offset = vOffset + k2;
                let x2;
                if (k2 === -d || (k2 !== d && v2[k2Offset - 1] < v2[k2Offset + 1])) {
                    x2 = v2[k2Offset + 1];
                }
                else {
                    x2 = v2[k2Offset - 1] + 1;
                }
                let y2 = x2 - k2;
                while (x2 < text1Length
                    && y2 < text2Length
                    && text1.charAt(text1Length - x2 - 1) === text2.charAt(text2Length - y2 - 1)) {
                    x2++;
                    y2++;
                }
                v2[k2Offset] = x2;
                if (x2 > text1Length) {
                    k2End += 2;
                }
                else if (y2 > text2Length) {
                    k2Start += 2;
                }
                else if (!front) {
                    const k1Offset = vOffset + delta - k2;
                    if (k1Offset >= 0 && k1Offset < vLength && v1[k1Offset] !== -1) {
                        const x1 = v1[k1Offset];
                        const y1 = vOffset + x1 - k1Offset;
                        x2 = text1Length - x2;
                        if (x1 >= x2) {
                            return this.diff_bisectSplit_(text1, text2, x1, y1, deadline);
                        }
                    }
                }
            }
        }
        return [
            [DiffOperation.DIFF_DELETE, text1],
            [DiffOperation.DIFF_INSERT, text2]
        ];
    }
    diff_bisectSplit_(text1, text2, x, y, deadline) {
        const text1A = text1.substring(0, x);
        const text2A = text2.substring(0, y);
        const text1B = text1.substring(x);
        const text2B = text2.substring(y);
        const diffsA = this.diff_main(text1A, text2A, false, deadline);
        const diffsB = this.diff_main(text1B, text2B, false, deadline);
        return diffsA.concat(diffsB);
    }
    diff_linesToCharsMunge_(text, lineArray, lineHash, maxLines) {
        let chars = "";
        let lineStart = 0;
        let lineEnd = -1;
        let lineArrayLength = lineArray.length;
        while (lineEnd < text.length - 1) {
            lineEnd = text.indexOf("\n", lineStart);
            if (lineEnd === -1) {
                lineEnd = text.length - 1;
            }
            let line = text.substring(lineStart, lineEnd + 1);
            if (lineHash.hasOwnProperty
                ? lineHash.hasOwnProperty(line)
                : (lineHash[line] !== undefined)) {
                chars += String.fromCharCode(lineHash[line]);
            }
            else {
                if (lineArrayLength === maxLines) {
                    line = text.substring(lineStart);
                    lineEnd = text.length;
                }
                chars += String.fromCharCode(lineArrayLength);
                lineHash[line] = lineArrayLength;
                lineArray[lineArrayLength++] = line;
            }
            lineStart = lineEnd + 1;
        }
        return chars;
    }
    diff_commonOverlap_(text1, text2) {
        const text1Length = text1.length;
        const text2Length = text2.length;
        if (text1Length === 0 || text2Length === 0) {
            return 0;
        }
        if (text1Length > text2Length) {
            text1 = text1.substring(text1Length - text2Length);
        }
        else if (text1Length < text2Length) {
            text2 = text2.substring(0, text1Length);
        }
        const textLength = math.min(text1Length, text2Length);
        if (text1 === text2) {
            return textLength;
        }
        let best = 0;
        let length = 1;
        while (true) {
            const pattern = text1.substring(textLength - length);
            const found = text2.indexOf(pattern);
            if (found === -1) {
                return best;
            }
            length += found;
            if (found === 0 ||
                text1.substring(textLength - length) === text2.substring(0, length)) {
                best = length;
                length++;
            }
        }
    }
    diff_halfMatch_(text1, text2) {
        if (this.diffTimeout <= 0) {
            return null;
        }
        const longtext = text1.length > text2.length ? text1 : text2;
        const shorttext = text1.length > text2.length ? text2 : text1;
        if (longtext.length < 4 || shorttext.length * 2 < longtext.length) {
            return null;
        }
        const hm1 = this.diff_halfMatchI_(longtext, shorttext, Math.ceil(longtext.length / 4));
        const hm2 = this.diff_halfMatchI_(longtext, shorttext, Math.ceil(longtext.length / 2));
        let hm;
        if (!hm1 && !hm2) {
            return null;
        }
        else if (!hm2) {
            hm = hm1;
        }
        else if (!hm1) {
            hm = hm2;
        }
        else {
            hm = hm1[4].length > hm2[4].length ? hm1 : hm2;
        }
        let text1A;
        let text1B;
        let text2A;
        let text2B;
        const midCommon = hm[4];
        if (text1.length > text2.length) {
            text1A = hm[0];
            text1B = hm[1];
            text2A = hm[2];
            text2B = hm[3];
        }
        else {
            text2A = hm[0];
            text2B = hm[1];
            text1A = hm[2];
            text1B = hm[3];
        }
        return [text1A, text1B, text2A, text2B, midCommon];
    }
    diff_halfMatchI_(longtext, shorttext, i) {
        const seed = longtext.substring(i, i + Math.floor(longtext.length / 4));
        let bestCommon = "";
        let bestLongtextA;
        let bestLongtextB;
        let bestShorttextA;
        let bestShorttextB;
        let j = shorttext.indexOf(seed, 0);
        while (j !== -1) {
            const prefixLength = this.diff_commonPrefix(longtext.substring(i), shorttext.substring(j));
            const suffixLength = this.diff_commonSuffix(longtext.substring(0, i), shorttext.substring(0, j));
            if (bestCommon.length < suffixLength + prefixLength) {
                bestCommon = shorttext.substring(j - suffixLength, j)
                    + shorttext.substring(j, j + prefixLength);
                bestLongtextA = longtext.substring(0, i - suffixLength);
                bestLongtextB = longtext.substring(i + prefixLength);
                bestShorttextA = shorttext.substring(0, j - suffixLength);
                bestShorttextB = shorttext.substring(j + prefixLength);
            }
            j = shorttext.indexOf(seed, j + 1);
        }
        if (bestCommon.length * 2 >= longtext.length) {
            return [
                bestLongtextA,
                bestLongtextB,
                bestShorttextA,
                bestShorttextB,
                bestCommon
            ];
        }
        return null;
    }
    diff_cleanupSemanticScore_(one, two) {
        if (!one || !two) {
            return 6;
        }
        const char1 = one.charAt(one.length - 1);
        const char2 = two.charAt(0);
        const nonAlphaNumeric1 = char1.match(NON_ALPHA_NUMERIC_REGEX);
        const nonAlphaNumeric2 = char2.match(NON_ALPHA_NUMERIC_REGEX);
        const whitespace1 = nonAlphaNumeric1 && char1.match(WHITESPACE_REGEX);
        const whitespace2 = nonAlphaNumeric2 && char2.match(WHITESPACE_REGEX);
        const lineBreak1 = whitespace1 && char1.match(LINEBREAK_REGEX);
        const lineBreak2 = whitespace2 && char2.match(LINEBREAK_REGEX);
        const blankLine1 = lineBreak1 && one.match(BLANKLINE_END_REGEX);
        const blankLine2 = lineBreak2 && two.match(BLANKLINE_START_REGEX);
        if (blankLine1 || blankLine2) {
            return 5;
        }
        else if (lineBreak1 || lineBreak2) {
            return 4;
        }
        else if (nonAlphaNumeric1 && !whitespace1 && whitespace2) {
            return 3;
        }
        else if (whitespace1 || whitespace2) {
            return 2;
        }
        else if (nonAlphaNumeric1 || nonAlphaNumeric2) {
            return 1;
        }
        return 0;
    }
    match_bitap_(text, pattern, loc) {
        if (pattern.length > this.matchMaxBits) {
            throw new Error("Pattern too long for this browser");
        }
        const s = this.match_alphabet_(pattern);
        let scoreThreshold = this.matchThreshold;
        let bestLoc = text.indexOf(pattern, loc);
        if (bestLoc !== -1) {
            scoreThreshold = math.min(this.match_bitapScore_(0, bestLoc, pattern, loc), scoreThreshold);
            bestLoc = text.lastIndexOf(pattern, loc + pattern.length);
            if (bestLoc !== -1) {
                scoreThreshold = math.min(this.match_bitapScore_(0, bestLoc, pattern, loc), scoreThreshold);
            }
        }
        const matchmask = 1 << (pattern.length - 1);
        bestLoc = -1;
        let binMin;
        let binMid;
        let binMax = pattern.length + text.length;
        let lastRD;
        for (let d = 0; d < pattern.length; d++) {
            binMin = 0;
            binMid = binMax;
            while (binMin < binMid) {
                if (this.match_bitapScore_(d, loc + binMid, pattern, loc) <= scoreThreshold) {
                    binMin = binMid;
                }
                else {
                    binMax = binMid;
                }
                binMid = Math.floor((binMax - binMin) / 2 + binMin);
            }
            binMax = binMid;
            let start = math.max(1, loc - binMid + 1);
            const finish = math.min(loc + binMid, text.length) + pattern.length;
            const rd = Array(finish + 2);
            rd[finish + 1] = (1 << d) - 1;
            for (let j = finish; j >= start; j--) {
                const charMatch = s[text.charAt(j - 1)];
                if (d === 0) {
                    rd[j] = ((rd[j + 1] << 1) | 1) & charMatch;
                }
                else {
                    rd[j] = (((rd[j + 1] << 1) | 1) & charMatch) |
                        (((lastRD[j + 1] | lastRD[j]) << 1) | 1) |
                        lastRD[j + 1];
                }
                if (rd[j] & matchmask) {
                    const score = this.match_bitapScore_(d, j - 1, pattern, loc);
                    if (score <= scoreThreshold) {
                        scoreThreshold = score;
                        bestLoc = j - 1;
                        if (bestLoc > loc) {
                            start = math.max(1, 2 * loc - bestLoc);
                        }
                        else {
                            break;
                        }
                    }
                }
            }
            if (this.match_bitapScore_(d + 1, loc, pattern, loc) > scoreThreshold) {
                break;
            }
            lastRD = rd;
        }
        return bestLoc;
    }
    match_bitapScore_(e, x, pattern, loc) {
        const accuracy = e / pattern.length;
        const proximity = Math.abs(loc - x);
        if (!this.matchDistance) {
            return proximity ? 1.0 : accuracy;
        }
        return accuracy + (proximity / this.matchDistance);
    }
    match_alphabet_(pattern) {
        const s = {};
        for (let i = 0; i < pattern.length; i++) {
            s[pattern.charAt(i)] = 0;
        }
        for (let i = 0; i < pattern.length; i++) {
            s[pattern.charAt(i)] |= 1 << (pattern.length - i - 1);
        }
        return s;
    }
    patch_addContext_(patch, text) {
        if (text.length === 0) {
            return;
        }
        if (patch.start2 == null) {
            throw Error("patch not initialized");
        }
        let pattern = text.substring(patch.start2, patch.start2 + patch.length1);
        let padding = 0;
        while (text.indexOf(pattern) !== text.lastIndexOf(pattern) &&
            pattern.length < (this.matchMaxBits - this.patchMargin - this.patchMargin)) {
            padding += this.patchMargin;
            pattern = text.substring(patch.start2 - padding, patch.start2 + patch.length1 + padding);
        }
        padding += this.patchMargin;
        const prefix = text.substring(patch.start2 - padding, patch.start2);
        if (prefix) {
            patch.diffs.unshift([DiffOperation.DIFF_EQUAL, prefix]);
        }
        const suffix = text.substring(patch.start2 + patch.length1, patch.start2 + patch.length1 + padding);
        if (suffix) {
            patch.diffs.push([DiffOperation.DIFF_EQUAL, suffix]);
        }
        patch.start1 -= prefix.length;
        patch.start2 -= prefix.length;
        patch.length1 += prefix.length + suffix.length;
        patch.length2 += prefix.length + suffix.length;
    }
}

;// ./node_modules/diff-match-patch-typescript/dist/es/core/index.js



;// ./node_modules/diff-match-patch-typescript/dist/es/index.js




/***/ },

/***/ 74685
(__unused_webpack_module, exports) {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
/**
 * Fetches the element in a string format
 */
var ElementSelector = /** @class */ (function () {
    function ElementSelector() {
    }
    ElementSelector.prototype.getSelector = function (el) {
        el.classList.remove('selectorgadget_selected');
        return el.outerHTML.replace(/\"/g, "\'");
    };
    return ElementSelector;
}());
exports["default"] = ElementSelector;


/***/ },

/***/ 78889
(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.AttributeSelector = void 0;
var diff_match_patch_typescript_1 = __webpack_require__(72560);
/**
 * Generates a selector for the hierarchy of the target element from DOM
 */
var AttributeSelector = /** @class */ (function () {
    function AttributeSelector() {
    }
    AttributeSelector.prototype.getSelector = function (el) {
        var hierarchy = [];
        var parentEl = el;
        while (parentEl && parentEl.tagName.toLowerCase() !== 'html') {
            var attr = (parentEl.tagName) ? parentEl.tagName.toLowerCase() : '';
            var map = (parentEl.attributes) ? parentEl.attributes : [];
            for (var _i = 0, map_1 = map; _i < map_1.length; _i++) {
                var mp = map_1[_i];
                if (!/click|style|\-|href|src|on\w+/g.test(mp.name)) {
                    if (mp.name === 'class') {
                        var classes = mp.value.split(' ');
                        for (var _a = 0, classes_1 = classes; _a < classes_1.length; _a++) {
                            var sClass = classes_1[_a];
                            // Can remove the selectorgadget_ matcher from regex when we are done with the front-end part of the selector tool
                            if (sClass !== '' && !/\:|\:\/\/|[\(\)\$\{\}]|axiom-matched|axiom-suggested-group|axiom-link|axiom-download|axiom-sel-\S+|selectorgadget_\w+/g.test(sClass)) {
                                attr += '[class~="' + sClass + '"]';
                            }
                        }
                    }
                    else {
                        if (!/value|data|\[|\]/gi.test(mp.name) && mp.value !== '' && !/\:|\:\/\//gi.test(mp.value)) {
                            attr += '[' + mp.name + '="' + mp.value.replace(/\"/g, '\\"') + '"]';
                        }
                    }
                }
            }
            hierarchy.unshift((attr === '') ? parentEl.tagName.toLowerCase() : attr);
            parentEl = parentEl.parentElement;
        }
        // Useful sanity test - commented out because it shouldn't run in production
        /*for (let h of hierarchy) {
            try {
                document.querySelectorAll(h)
            } catch (e) {
                console.error("failed querySelector: ", h)
            }
        }*/
        return hierarchy.join(' > ');
    };
    /**
     * Fetches the group selector out of a list of attribute selector
     *
     */
    AttributeSelector.prototype.groupAttributeSelectors = function (selectors) {
        var commonAncestor = selectors[0];
        if (selectors.length > 1) {
            var dmp = new diff_match_patch_typescript_1.DiffMatchPatch();
            for (var i = 1; i < selectors.length; i++) {
                var tempDiff = [];
                tempDiff = dmp.diff_main(commonAncestor, selectors[i]);
                commonAncestor = '';
                for (var _i = 0, tempDiff_1 = tempDiff; _i < tempDiff_1.length; _i++) {
                    var diff = tempDiff_1[_i];
                    if (diff[0] === 0) {
                        commonAncestor += diff[1];
                    }
                    if (commonAncestor !== '' && diff[0] !== 0) {
                        break;
                    }
                }
            }
        }
        var cleanedGroup = this.cleanupGroupingSelector(commonAncestor);
        while (this.groupSelectorValidator(cleanedGroup, selectors) !== true) {
            // trims away the last element from the selector
            cleanedGroup = cleanedGroup.replace(/(\s>\s)(\S*\[\S*\]|\S)$/gm, '');
        }
        return cleanedGroup;
    };
    /**
     * Validates whether the group selector selects targetted elements
     *
     * @param groupSelector
     * @param elementSelectors
     */
    AttributeSelector.prototype.groupSelectorValidator = function (groupSelector, elementSelectors) {
        var groupEl = document.querySelectorAll(groupSelector);
        var elementCount = elementSelectors.length;
        var elementSelectorsString = elementSelectors.join(', ');
        var elementsWithinGroup = 0;
        groupEl.forEach(function (el) {
            var items = el.querySelectorAll(elementSelectorsString);
            if (items.length >= 0) {
                elementsWithinGroup = items.length;
            }
        });
        // Would work for cases where selections are made within a single list item
        if (elementsWithinGroup >= elementCount) {
            return true;
        }
        else {
            return false;
        }
    };
    /**
     * Cleans selector string from incorrect string
     *
     * @param selector
     */
    AttributeSelector.prototype.cleanupGroupingSelector = function (selector) {
        var cleanedSelector = selector;
        var lastCleanedCss = null;
        while (lastCleanedCss !== cleanedSelector) {
            lastCleanedCss = cleanedSelector;
            cleanedSelector = cleanedSelector
                // removes empty class attributes
                // [class~=""]
                .replace(/\[class\~\=\"\"\]/gm, '')
                // removes ' > ' from end of string
                .replace(/(\s*\>+\s*)$/gm, '')
                // removes empty attribute selections 
                // > [class~="xso"] > 
                .replace(/(\>\s*\[\S*\]\s*\>\s*)/gm, '')
                // removes dangling attributes at the end of string
                //  > div[class~=""
                .replace(/(\s*\>\s*\S*\[\S*\s*(?<!\]))$/gm, '');
        }
        return cleanedSelector;
    };
    return AttributeSelector;
}());
exports.AttributeSelector = AttributeSelector;


/***/ },

/***/ 89362
(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.HierarchyActions = void 0;
var AttributeSelector_1 = __webpack_require__(78889);
var HierarchyActions = /** @class */ (function () {
    function HierarchyActions() {
        this.attributeSelector = new AttributeSelector_1.AttributeSelector();
    }
    /**
     * Takes 2 collections of elements
     * Returns a single AtrributeSelector that will:
     * -select all includeElements
     * -select none of the excludeElements
     *
     * @param includeElements Array of Elements to be included in the selection
     * @param excludeElements Array of Elements to be excluded from the selection
     *
     * @returns String to be used as a selector compatable with document.querySelectorAll(selector: String)
     * @example ':-webkit-any(div, body):not([id="g2"]) > :-webkit-any(article, section)[class~="post"]:not([id="a4"]) > h3:not([id="h4"])'
     *
     */
    HierarchyActions.prototype.getCombined = function (document, includeElements, excludeElements, type) {
        if (includeElements.length === 0) {
            return '';
        }
        var includeSelectors = this.getAsAttributeSelectors(includeElements);
        var excludeSelectors = this.getAsAttributeSelectors(excludeElements);
        var inSections = [];
        var exSections = [];
        for (var _i = 0, includeSelectors_1 = includeSelectors; _i < includeSelectors_1.length; _i++) {
            var selector = includeSelectors_1[_i];
            inSections.push(this.splitHierarchyString(selector));
        }
        for (var _a = 0, excludeSelectors_1 = excludeSelectors; _a < excludeSelectors_1.length; _a++) {
            var selector = excludeSelectors_1[_a];
            exSections.push(this.splitHierarchyString(selector));
        }
        var allSections = [].concat(inSections, exSections);
        var levels = [];
        // The tags arrays are ordered with the highest element in the tree first, and this causes things to go out of sync when selectors are not 
        // the same length. For example, body > div > span and body > div will be compared as [[span, div], [div, body], [body, undefined]].
        // To fix this we add a new reversed version of the tags and modifers to each of the objects we check.
        for (var _b = 0, allSections_1 = allSections; _b < allSections_1.length; _b++) {
            var as = allSections_1[_b];
            as.tagsReversed = as.tags.slice().reverse();
        }
        for (var _c = 0, inSections_1 = inSections; _c < inSections_1.length; _c++) {
            var is = inSections_1[_c];
            is.tagsReversed = is.tags.slice().reverse();
        }
        // Loop through the tags. This entire loop is inside out. We are looping through the inner array 
        // (which represents the parts of the hierarchy for each selector), as
        // the outer loop, and the outer array (which represents each selector) as the inner loop. The reason for this is so we can compare the
        // individual parts of the two selector strings.
        var largestTagIndex = 0;
        for (var _d = 0, allSections_2 = allSections; _d < allSections_2.length; _d++) {
            var section = allSections_2[_d];
            if (section.tagsReversed.length > largestTagIndex) {
                largestTagIndex = section.tags.length;
            }
        }
        for (var index = 0; index < largestTagIndex; index++) {
            // We loop through the outer loop and get an array of tags and modifiers for each section for this part of the hierarchy
            var tags = [];
            for (var _e = 0, inSections_2 = inSections; _e < inSections_2.length; _e++) {
                var section = inSections_2[_e];
                // get tags
                if (section.tagsReversed[index]) {
                    tags.push(section.tagsReversed[index]);
                }
            }
            if (tags.length === 0) {
                return '';
            }
            var tag = '';
            if (tags.length === inSections.length) {
                if (tags.length === 1) {
                    tag = tags[0];
                }
                else {
                    var reducedTags = [];
                    for (var _f = 0, tags_1 = tags; _f < tags_1.length; _f++) {
                        var t = tags_1[_f];
                        if (reducedTags.indexOf(t) === -1) {
                            reducedTags.push(t);
                        }
                    }
                    if (reducedTags.length === 1) {
                        tag = reducedTags[0];
                    }
                    else {
                        tag = ":-webkit-any(" + reducedTags.join(', ') + ")";
                    }
                }
                levels.push(tag);
            }
        }
        var combinedSelector = '';
        combinedSelector = levels.join(' > ');
        combinedSelector = combinedSelector.replace(/\n/g, '');
        combinedSelector = combinedSelector.replace(/\s\s/g, ' ');
        combinedSelector = combinedSelector.replace(/\[class~="[^\S]*"\]/g, '');
        if (type === 'selector') {
            var selectorWithNthSpecifiers = this.applyNthSpecifiers(document, combinedSelector, includeElements, excludeElements);
            // If this selector selects the same number of results as the previous one, we don't use it; it's likely too specific.
            if (document.querySelectorAll(combinedSelector).length !== document.querySelectorAll(selectorWithNthSpecifiers).length) {
                combinedSelector = selectorWithNthSpecifiers;
            }
        }
        var matchedElements = [];
        try {
            matchedElements = Array.from(document.querySelectorAll(combinedSelector));
        }
        catch (e) {
        }
        combinedSelector = this.trimAttributes(document, combinedSelector, matchedElements, excludeElements);
        combinedSelector = this.trimHierarchy(document, combinedSelector, matchedElements, excludeElements);
        return combinedSelector.replace(/\:not\(\)/g, ""); // strip empty :not() attributes
    };
    HierarchyActions.prototype.excludedMatches = function (document, selector, excludedElements) {
        //get all elements that are currently matched by the combined selector
        var matching = [];
        try {
            matching = Array.from(document.querySelectorAll(selector));
        }
        catch (e) {
        }
        //check for any elements in excludeElements that matched
        return matching.filter(function (el) {
            return excludedElements.includes(el);
        });
    };
    HierarchyActions.prototype.misMatches = function (document, selector, excludedElements) {
        //get all elements that are currently matched by the combined selector
        var matching = [];
        try {
            matching = Array.from(document.querySelectorAll(selector));
        }
        catch (e) {
        }
        //check for any elements not includeedElements that matched
        return matching.filter(function (el) {
            return excludedElements.includes(el);
        });
    };
    HierarchyActions.prototype.overSelected = function (document, selector, elementsToMatch) {
        //get all elements that are currently matched by the combined selector
        var matching = [];
        try {
            matching = Array.from(document.querySelectorAll(selector));
        }
        catch (e) {
        }
        //check for any extra elements sneaking in
        return matching.filter(function (el) {
            return !elementsToMatch.includes(el);
        });
    };
    HierarchyActions.prototype.missingElements = function (document, selector, elementsToMatch) {
        //get all elements that are currently matched by the combined selector
        var matching = [];
        try {
            matching = Array.from(document.querySelectorAll(selector));
        }
        catch (e) {
        }
        //check for any missing elements
        return elementsToMatch.filter(function (el) {
            return !matching.includes(el);
        });
    };
    HierarchyActions.prototype.trimHierarchy = function (document, combinedSelector, includeElements, excludeElements) {
        var selectorLevels = combinedSelector.split(' > ');
        var trimmedLength = selectorLevels.length;
        var trimmedSelector = selectorLevels.slice(selectorLevels.length - trimmedLength, selectorLevels.length).join(' > ');
        while (trimmedLength > 0 && !this.missingElements(document, trimmedSelector, includeElements).length && !this.misMatches(document, trimmedSelector, excludeElements).length && !this.overSelected(document, trimmedSelector, includeElements).length) {
            trimmedLength--;
            trimmedSelector = selectorLevels.slice(selectorLevels.length - trimmedLength, selectorLevels.length).join(' > ');
            if (/\:not\(\:nth/.test(selectorLevels[selectorLevels.length - trimmedLength])) { // here we have a user specified exclusion and so we shouldn't strip it out
                return selectorLevels.slice(selectorLevels.length - (trimmedLength), selectorLevels.length).join(' > ');
            }
        }
        return selectorLevels.slice(selectorLevels.length - (trimmedLength + 1), selectorLevels.length).join(' > ');
    };
    HierarchyActions.prototype.trimSelector = function (document, selector, includeElements, excludeElements) {
        var selectorLevels = selector.split(' > ');
        var trimmedLength = selectorLevels.length;
        var trimmedSelector = selectorLevels.slice(selectorLevels.length - trimmedLength, selectorLevels.length).join(' > ');
        while (trimmedLength < selectorLevels.length - 1 && !this.missingElements(document, trimmedSelector, includeElements).length && !this.misMatches(document, trimmedSelector, excludeElements).length) {
            trimmedLength++;
            trimmedSelector = selectorLevels.slice(selectorLevels.length - trimmedLength, selectorLevels.length).join(' > ');
            trimmedSelector = this.trimAttributes(document, trimmedSelector, includeElements, excludeElements);
        }
        return selectorLevels.slice(selectorLevels.length - (trimmedLength + 1), selectorLevels.length).join(' > ');
    };
    HierarchyActions.prototype.trimAttributes = function (document, combinedSelector, includeElements, excludeElements) {
        var allAttributes = combinedSelector.match(/\[[^\s\[\]]*\]/g);
        if (allAttributes && allAttributes.length) {
            for (var _i = 0, allAttributes_1 = allAttributes; _i < allAttributes_1.length; _i++) {
                var attribute = allAttributes_1[_i];
                attribute = attribute.replace(/\+/g, "\\+");
                // we will make a selector for testing where all occurances of attribute are stripped out
                var testSelector = combinedSelector.replace(new RegExp(attribute.replace('[', '\\[').replace(']', '\\]'), 'g'), "");
                if (!this.missingElements(document, testSelector, includeElements).length && !this.misMatches(document, testSelector, excludeElements).length && !this.overSelected(document, testSelector, includeElements).length) {
                    combinedSelector = testSelector;
                }
            }
        }
        return combinedSelector;
    };
    HierarchyActions.prototype.applyNthSpecifiers = function (document, combinedSelector, includeElements, excludeElements) {
        // ensure there are no hidden elements selected by the combinedSelector before adding the nthSelectors
        var initialMatches = Array.from(document.querySelectorAll(combinedSelector));
        var invisible = initialMatches.filter(function (el) {
            return !(includeElements.includes(el) || $(el).filter(':visible').length);
        });
        var nthMods = [];
        // Pull out the number of siblings of the target element at each depth
        // "Inc Levels" and "Ex Levels" here are poorly named, but are basically the array of each selector's sibling counts, transposed.
        var inc_levels = [];
        for (var _i = 0, includeElements_1 = includeElements; _i < includeElements_1.length; _i++) {
            var include = includeElements_1[_i];
            var counts = treeCount(include);
            for (var level in counts) {
                if (Array.isArray(inc_levels[level])) {
                    inc_levels[level].push(counts[level]);
                }
                else {
                    inc_levels[level] = [counts[level]];
                }
            }
        }
        var exc_levels = [];
        for (var _a = 0, excludeElements_1 = excludeElements; _a < excludeElements_1.length; _a++) {
            var exclude = excludeElements_1[_a];
            var counts = treeCount(exclude);
            for (var level in counts) {
                if (Array.isArray(exc_levels[level])) {
                    exc_levels[level].push(counts[level]);
                }
                else {
                    exc_levels[level] = [counts[level]];
                }
            }
        }
        for (var level in inc_levels) {
            var inc_nth = inc_levels[level];
            var exc_nth = exc_levels[level];
            // This basically removes stuff from inc_nth that is in exc_nth, but is expressed needlessly generically.
            var unique_nth = getUnique(inc_nth, exc_nth);
            var nthMod = getNthMods({ include: inc_nth, exclude: unique_nth.exclude });
            nthMods[level] = (nthMod !== undefined) ? nthMod : '';
        }
        var split = combinedSelector.split(' > ');
        split.reverse();
        for (var level in split) {
            if (nthMods[level]) {
                split[level] += nthMods[level];
            }
        }
        split.reverse();
        return split.join(' > ');
        // 'HELPER' FUNCTIONS
        // Seriously these should not be nested 2 deep in the parent function, needs a refactor badly
        function treeCount(element) {
            var counts = [];
            var check = element;
            while (check.parentElement && check.tagName) {
                var count = countSiblings(check);
                counts.push(count);
                check = check.parentElement;
            }
            return counts;
        }
        function countSiblings(element) {
            var siblingCount = 1;
            var ofTypeCount = 1;
            var check = element;
            while (check.previousElementSibling && check.tagName) {
                siblingCount++;
                if (check.previousElementSibling.tagName === check.tagName) {
                    ofTypeCount++;
                }
                check = check.previousElementSibling;
            }
            return siblingCount;
        }
        // returns items in a that aren't in b and in b that aren't in a
        function getUnique(include, exclude) {
            var uniqueInclude = [];
            if (include && include.length) {
                if (exclude && exclude.length) {
                    uniqueInclude = include.filter(function (item) {
                        return !exclude.includes(item);
                    });
                }
                else { // there are no excludes specified and so all includes are unique
                    uniqueInclude = include;
                }
            }
            var uniqueExclude = [];
            if (exclude && exclude.length) {
                if (include && include.length) {
                    uniqueExclude = exclude.filter(function (item) {
                        return !include.includes(item);
                    });
                }
                else { // there are no includes specified and so all excludes are unique
                    uniqueExclude = exclude;
                }
            }
            return { include: uniqueInclude, exclude: uniqueExclude };
        }
        function getNthMods(sample) {
            var include = { series: sample.include, diffs: [], expandedSeries: [] };
            var exclude = { series: sample.exclude, diffs: [], expandedSeries: [] };
            // So a diff here is an array, containing the differences between each chosen element for that level of the hierarchy
            // For example, if elemnt 0 has selected the 2nd sibling at a particular level, and element 1 has the 3rd, this generates a diff of 1
            genDiffs(include);
            var includeMeta = findSeries(include.series, include.diffs);
            var pattern = getSeriesFormula(includeMeta);
            var includePattern;
            if (pattern) {
                includePattern = ":nth-child(".concat(pattern, ")");
            }
            genDiffs(exclude);
            exclude = findSeries(exclude.series, include.diffs);
            var excludePatterns = [];
            if (exclude.expandedSeries.length && exclude.diffs[0] !== undefined && exclude.series[0] !== undefined && !hasCommonItem(include.series, exclude.expandedSeries)) {
                // generate pattern
                var m = exclude.diffs[0];
                var c = exclude.series[0]; // use series so that any pattern starts with first excluded element
                var offset = (c > 0) ? "+".concat(c) : (c < 0) ? "".concat(c) : '';
                var pattern_1 = "".concat(m, "n").concat(offset);
                var exc_pattern = ":not(:nth-child(".concat(pattern_1, "))");
                if (!excludePatterns.includes(exc_pattern)) {
                    excludePatterns.push(exc_pattern);
                }
            }
            else {
                // generate nths
                for (var _i = 0, _a = exclude.series; _i < _a.length; _i++) {
                    var val = _a[_i];
                    var exc_pattern = ":not(:nth-child(".concat(val, "))");
                    if (!excludePatterns.includes(exc_pattern)) {
                        excludePatterns.push(exc_pattern);
                    }
                }
            }
            var nthMods = '';
            if (includePattern) {
                nthMods += includePattern;
            }
            if (excludePatterns.length) {
                nthMods += "".concat(excludePatterns.join(''));
            }
            return nthMods;
            // HELPER FUNCTIONS
            // Same anti-pattern as previously
            function genDiffs(set) {
                var diffs = [];
                var series = set.series.sort(function (a, b) {
                    return a - b;
                });
                for (var i = 0; i < series.length - 1; i++) {
                    var newDiff = series[i + 1] - series[i];
                    if (newDiff > 0 && !diffs.includes(newDiff)) {
                        diffs.push(newDiff);
                    }
                }
                set.diffs = diffs;
                set.sortedDiffs = diffs.sort(function (a, b) {
                    return a - b;
                });
            }
            function hasCommonItem(a, b) {
                var commonItem = false;
                for (var _i = 0, a_1 = a; _i < a_1.length; _i++) {
                    var item = a_1[_i];
                    if (b.includes(item)) {
                        commonItem = true;
                    }
                }
                return commonItem;
            }
            function allFoundIn(a, b) {
                for (var _i = 0, a_2 = a; _i < a_2.length; _i++) {
                    var item = a_2[_i];
                    if (!b.includes(item)) {
                        return false;
                    }
                }
                return true;
            }
            function getExpandedSeries(series, stepValue) {
                if (!series.length) {
                    return [];
                }
                var expandedSeries = [];
                var sortedSeries = JSON.parse(JSON.stringify(series));
                sortedSeries.sort(function (b, a) {
                    var diff = b - a;
                    return diff;
                });
                var seriesLimit = sortedSeries[sortedSeries.length - 1];
                var seriesStart = seriesLimit % stepValue;
                expandedSeries.push(seriesLimit);
                while (expandedSeries[0] > seriesStart) {
                    expandedSeries.unshift(expandedSeries[0] - stepValue);
                }
                return expandedSeries;
            }
            function findSeries(series, diffs) {
                var result = { series: series, expandedSeries: [], diffs: [] };
                if (!diffs.length) {
                    result.expandedSeries = [series[0]];
                }
                else {
                    var stepValue = diffs[0];
                    var done = false;
                    while (stepValue > 0 && !done) {
                        var testSeries = getExpandedSeries(series, stepValue);
                        if (allFoundIn(series, testSeries)) {
                            result = { series: series, expandedSeries: testSeries, diffs: [stepValue] };
                            done = true;
                        }
                        else {
                            stepValue--;
                        }
                    }
                }
                return result;
            }
            function getSeriesFormula(setObject) {
                var m; // (multiplier)
                var c; // (x shift)
                // set m value (multiplier)
                if (!setObject.diffs.length) {
                    m = 0;
                }
                else {
                    m = setObject.diffs[0];
                }
                // set c value (x shift)
                if (m === 0) {
                    c = setObject.expandedSeries[0];
                    if (c) {
                        return "".concat(c);
                    }
                }
                else {
                    c = (setObject.expandedSeries[0] !== undefined) ? setObject.expandedSeries[0] - m : 0;
                }
                var nthDescriptor = "".concat(m, "n ");
                if (c !== 0) {
                    if (c > 0) {
                        nthDescriptor += '+';
                    }
                    nthDescriptor += "".concat(c);
                }
                return nthDescriptor;
            }
        }
    };
    /**
     * Takes an array of Elements and returns an Array of AttributeSelectors
     *
     * @param elements Array of type Elements
     *
     * @returns Array of AttributeSelectors
     * @example [
     *              'body > table[id="a1"] > tr[id="b2"] > div[id="c1"] > div[id="g1] > article[id="a2"][class~="post"] > h3[id="h2"]',
     *              'body > div[id="g3] > article[id="a9"][class~="post"] > h3[id="h9"]'
     *              'body > section[class~="post"] > h3[id="h10"]'
     *          ]
     */
    HierarchyActions.prototype.getAsAttributeSelectors = function (elements, document, excludeElements) {
        var attributeSelectors = [];
        for (var _i = 0, elements_1 = elements; _i < elements_1.length; _i++) {
            var el = elements_1[_i];
            if (typeof el === 'string' || !(Object.keys(el).length === 0 && el.constructor === Object)) {
                var selector = this.attributeSelector.getSelector(el);
                var trimmedSelector = (document === undefined) ? selector : this.trimAttributes(document, selector, [el], excludeElements);
                attributeSelectors.push(trimmedSelector);
            }
        }
        return attributeSelectors;
    };
    /**
     *
     * @param hierarchyString String based on the css hierachy selector
     *
     * @example splitHierarchyString('body > table[id="a1"] > tr[id="b1"] > div[id="c1"][class~="target"]:not(".sticky") > div[id="g1] > article[id="a1"][class~="post"] > h3[id="h1"]')
     *
     * @returns Object {
     *                    hierarchyString, (input param String)
     *                    tags,            (html tags from input string)
     *                    mods,            (css selectors applied to each html tag)
     *                    seperators       (hierarchy seperators as strings)
     *          }
     * @example {
     *      hierachyString: 'body > table[id="a1"] > tr[id="b1"] > div[id="c1"][class~="target"]:not(".sticky") > div[id="g1] > article[id="a1"][class~="post"] > h3[id="h1"]',
     *      tags: ['body', 'table', 'tr', 'div', 'div', 'article', 'h3']
     *      mods: ['', '[id="a1"]', '[id="b1"]', '', '[id="c1"][class~="target"]:not(".sticky")', '[id="g1]', '[id="a1"][class~="post"]', '[id="h1"]'],
     *      seperators: [' > ', ' > ', ' > ', ' > ', ' > ', ' > ']
     * }
     */
    HierarchyActions.prototype.splitHierarchyString = function (hierarchyString) {
        // get the seperator strings between each level
        var seperators = []; // a seperater per level e.g. ' > '
        var sections = hierarchyString.split(/[\s][\s]*/);
        for (var s = 0; s < sections.length - 1; s++) { // populate seperators
            seperators.push(' > ');
        }
        // Split the hierarchy into levels
        var levels = hierarchyString.split(' > ').reverse();
        // get the html tag and modifiers (attribute and alias selectors) at each level of the hierarchy
        var tags = []; // a html tag per level
        var mods = []; // a String with all modifier selector at each level
        for (var depth = 0; depth < levels.length; depth++) {
            tags[depth] = levels[depth].split(/[\[\:]/)[0];
            mods[depth] = levels[depth].substr(tags[depth].length);
        }
        return {
            hierarchyString: hierarchyString,
            tags: tags,
            mods: mods,
            seperators: seperators //TODO: redundant?
        };
    };
    /**
     * Takes a collection of arrays and compares the items in each array
     * return a collection of items that can be found in all the arrays provided
     *
     * @param arrays Array of Arrays
     *
     * @returns Array of items common to all arrays provided in the arrays param
     * @example getCommonItems([[1,2,3,4,5,6,7,8,9,10,11,12], [2,4,6,8,10,12], [4,8,12]])
     *
     * [4, 12]
     */
    HierarchyActions.prototype.getCommonItems = function (arrays) {
        if (arrays.length === 0) {
            return [];
        }
        if (arrays.length === 1) {
            return arrays[0];
        }
        var commonItems = [];
        var count = {};
        for (var _i = 0, arrays_1 = arrays; _i < arrays_1.length; _i++) {
            var a = arrays_1[_i];
            for (var i = 0; i < a.length; i++) {
                count[a[i]] = (count[a[i]] === undefined) ? count[a[i]] = 1 : count[a[i]] + 1;
            }
        }
        var counts = Object.values(count);
        var items = Object.keys(count);
        for (var c = 0; c < counts.length; c++) {
            if (counts[c] === arrays.length) { //item was found in all arrays
                commonItems.push(items[c]);
            }
        }
        return commonItems;
    };
    /**
     * Takes an array and a collection of arrays
     * and finds the items that are unique to the single Array
     * and items that are in the arrays but not in the single array
     *
     * @param singleArray Array of items
     * @param arrays Array of Array of items
     *
     * @example getDiff([3,6,9,12], [[2,4,6,8,10,12], [4,8,12]])
     *
     * @returns Object {
     *              unique, (Items unique to the array)
     *              missing, (Items each array in arrays but not in the sinlge array)
     *          }
     * @example {
     *      unique: [3,9],
     *      missing: [4,8]
     * }
     */
    HierarchyActions.prototype.getDiff = function (singleArray, arrays) {
        var unique = [];
        var missing = [];
        var common = this.getCommonItems(arrays);
        missing = common.filter(function (item) {
            return singleArray.indexOf(item) === -1;
        });
        for (var _i = 0, singleArray_1 = singleArray; _i < singleArray_1.length; _i++) {
            var item = singleArray_1[_i];
            var exclusive = true;
            for (var _a = 0, arrays_2 = arrays; _a < arrays_2.length; _a++) {
                var arr = arrays_2[_a];
                if (arr.indexOf(item) > -1) {
                    exclusive = false;
                }
            }
            if (exclusive) {
                unique.push(item);
            }
        }
        return { unique: unique, missing: missing };
    };
    HierarchyActions.prototype.selectorAtLevel = function (selector, level) {
        var levels = selector.split(' > ');
        var res = (levels.length - level > 0) ? levels.slice(0, levels.length - level).join(' > ') : undefined;
        return res;
    };
    HierarchyActions.prototype.testSelectorAtLevelSelectors = function (document, selector, allSelectors, groups) {
        var testGroup = document.querySelector(selector);
        var matches = [];
        try {
            matches = Array.from(testGroup.querySelectorAll(allSelectors));
        }
        catch (e) {
            // failing to use selector on element, no action required
        }
        for (var _i = 0, _a = groups[0]; _i < _a.length; _i++) {
            var el = _a[_i];
            if (!matches.includes(el)) {
                // testGroup is one step too large
                return false;
            }
        }
        return true;
    };
    HierarchyActions.prototype.testSelectorAtLevelGrouping = function (document, selector, allSelectors, groups) {
        var testGroup = document.querySelector(selector);
        var matches = [];
        try {
            matches = Array.from(testGroup.querySelectorAll(allSelectors));
        }
        catch (e) {
            // failing to use selector on element, no action required
        }
        for (var _i = 0, matches_1 = matches; _i < matches_1.length; _i++) {
            var match = matches_1[_i];
            if (!groups[0].includes(match)) {
                // testGroup is one step too large
                return true;
            }
        }
        return false;
    };
    HierarchyActions.prototype.findGroupSelectors = function (document, selectors, groups) {
        var allSelectors = selectors.join(',');
        var groupSelectors = [];
        for (var _i = 0, selectors_1 = selectors; _i < selectors_1.length; _i++) {
            var selector = selectors_1[_i];
            var trimmed = 'body';
            var level = 0;
            var done = false;
            while (trimmed !== undefined && !done) {
                trimmed = this.selectorAtLevel(selector, level);
                var testA = this.testSelectorAtLevelSelectors(document, trimmed, allSelectors, groups);
                var testB = this.testSelectorAtLevelGrouping(document, trimmed, allSelectors, groups);
                if (testA && !testB) {
                    done = true;
                }
                else {
                    if (testB) {
                        trimmed = this.selectorAtLevel(selector, level - 1);
                        done = true;
                    }
                    else {
                        level++;
                    }
                }
            }
            groupSelectors.push(trimmed);
        }
        //TODO: remove duplicates before returning
        return groupSelectors;
    };
    return HierarchyActions;
}());
exports.HierarchyActions = HierarchyActions;


/***/ },

/***/ 99066
(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
__webpack_require__(2205);
/**
 * Generates a selector for the hierarchy of the target element from DOM
 */
var HierarchySelector = /** @class */ (function () {
    function HierarchySelector() {
    }
    HierarchySelector.prototype.getSelector = function (el) {
        var stack = [];
        // Bottom-up selector generator algorithm
        while (el.parentNode != null) {
            // Total count of siblings for a group
            var sibCount = 0;
            // Index of the sibling we are targetting
            var sibIndex = 0;
            for (var i = 0; i < el.parentNode.childNodes.length; i++) {
                var sib = el.parentNode.childNodes[i];
                /**
                 * Avoid adding axiom injected toolbar components from messing the heirarchy of the selector
                 * TODO: More specific; we'll define a particular AXIOM hash and check for that (in env)
                 */
                if (sib.nodeType === Node.ELEMENT_NODE) {
                    if (sib.id && (typeof sib.id === 'string' && sib.id.includes('axiom'))) {
                        continue;
                    }
                    if (sib.nodeName === el.nodeName) {
                        if (sib === el) {
                            sibIndex = sibCount;
                        }
                        sibCount++;
                    }
                }
            }
            if (sibCount > 1) {
                if (sibIndex > 1 && (sibIndex + 1 === el.parentNode.childNodes.length || $(el).is(':nth-last-of-type(1)'))) {
                    // If last child of a group, use the following snippet instead of `nth-of-type(sibIndex+1)`
                    stack.unshift(el.nodeName.toLowerCase() + ':nth-last-of-type(1)');
                }
                else {
                    stack.unshift(el.nodeName.toLowerCase() + ':nth-of-type(' + (sibIndex + 1) + ')');
                }
            }
            else {
                stack.unshift(el.nodeName.toLowerCase());
            }
            el = el.parentNode;
        }
        // removes the html element
        stack.shift();
        // Test the selector and trim it if it's working fine
        var selector = stack.join(' > ');
        var firstEl = null;
        while (document.querySelectorAll(selector).length === 1 && stack.length >= 2) {
            firstEl = stack.shift();
            selector = stack.join(' > ');
        }
        // This is needed because the iframe code is not feature complete
        if (firstEl) {
            stack.unshift(firstEl);
        }
        if (stack.length > 0) {
            // joins each tags of the selector by space (children element)
            return stack.join(' > ');
        }
        else {
            // failed to fetch the selector
            return false;
        }
    };
    HierarchySelector.prototype.getSelectorForSizzle = function (el) {
        var stack = [];
        // Bottom-up selector generator algorithm
        while (el.parentNode != null) {
            // Total count of siblings for a group
            var sibCount = 0;
            // Index of the sibling we are targetting
            var sibIndex = 0;
            for (var i = 0; i < el.parentNode.childNodes.length; i++) {
                var sib = el.parentNode.childNodes[i];
                /**
                 * Avoid adding axiom injected toolbar components from messing the heirarchy of the selector
                 * TODO: More specific; we'll define a particular AXIOM hash and check for that (in env)
                 */
                if (sib.nodeType === Node.ELEMENT_NODE) {
                    if (sib.id && (typeof sib.id === 'string' && sib.id.includes('axiom'))) {
                        continue;
                    }
                    if (sib === el) {
                        sibIndex = sibCount;
                    }
                    sibCount++;
                }
            }
            if (sibCount > 1) {
                var path = el.nodeName.toLowerCase();
                // Add the classname to node element when it is requested
                if (el.className) {
                    var refs = el.className.split(" ");
                    for (var i = 0, len = refs.length; i < len; i++) {
                        var cssName = refs[i];
                        var escaped = this.escapeCssNames(cssName);
                        escaped = CSS.escape(escaped);
                        if (cssName && escaped.length > 0) {
                            path += '.' + escaped;
                        }
                    }
                }
                if (sibIndex > 1) {
                    path += ':nth-child(' + (sibIndex + 1) + ')';
                }
                stack.unshift(path);
            }
            else {
                stack.unshift(el.nodeName.toLowerCase());
            }
            el = el.parentNode;
        }
        // removes the html element
        stack = stack.slice(1);
        if (stack.length > 0) {
            // joins each tags of the selector by space (children element)
            return stack.join(' > ');
        }
        else {
            // failed to fetch the selector
            return false;
        }
    };
    HierarchySelector.prototype.escapeCssNames = function (name) {
        if (name) {
            try {
                return name.replace(/\bselectorgadget_\w+\b/g, '').replace(/\\/g, '\\\\').replace(/[\#\;\&\,\.\+\*\~\'\:\"\!\^\$\[\]\(\)\=\>\|\/]/g, function (e) {
                    return '\\' + e;
                }).replace(/\s+/, '');
            }
            catch (e) {
                if (window.console) {
                    console.log('---');
                    console.log("exception in escapeCssNames");
                    console.log(name);
                    console.log('---');
                }
                return '';
            }
        }
        else {
            return '';
        }
    };
    return HierarchySelector;
}());
exports["default"] = HierarchySelector;


/***/ }

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/global */
/******/ 	(() => {
/******/ 		__webpack_require__.g = (function() {
/******/ 			if (typeof globalThis === 'object') return globalThis;
/******/ 			try {
/******/ 				return this || new Function('return this')();
/******/ 			} catch (e) {
/******/ 				if (typeof window === 'object') return window;
/******/ 			}
/******/ 		})();
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module is referenced by other modules so it can't be inlined
/******/ 	var __webpack_exports__ = __webpack_require__(33729);
/******/ 	
/******/ })()
;
//# sourceMappingURL=axiomselector.js.map